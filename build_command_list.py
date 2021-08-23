import ast
import os

COGS_PATH = './bot/cogs'
DOC_PATH = './command_list.md'
PREFIX = '+'
VERSION = '1.32.8.16'

if os.path.isfile(DOC_PATH):
    os.remove(DOC_PATH)


def make_md_header(filename):
    with open(DOC_PATH, mode='a', encoding='utf-8') as file:
        file.write(f'## {filename}\n\n')


def insert_docu(cmd: dict):
    cmd_usage = '+'
    if cmd["has_parent"]:
        cmd_usage += f'{cmd["group_name"]} {cmd["cmd_name"]}'
    else:
        cmd_usage += f'{cmd["cmd_name"]}'

    if cmd["cmd_args"]:
        args = ' '.join([f'<{arg}>' for arg in cmd["cmd_args"]])
        cmd_usage += f' {args}'

    cmd_auths = ''
    if not cmd["group_auths"]:
        if not cmd["cmd_auths"]:
            cmd_auths = '`無`'
        else:
            cmd_auths = ' '.join([f'`{auth}`' for auth in cmd["cmd_auths"]])
    else:
        cmd_auths = ' '.join([f'`{auth}`' for auth in cmd["group_auths"]])

    cmd_descr = []
    cmd_args_descr = []

    cmd_area = False
    cmd["cmd_doc"] = cmd["cmd_doc"].split('\n')
    cmd["cmd_doc"] = [item.strip('  ') for item in cmd["cmd_doc"] if item.strip() and item != 'cmd']

    for item in cmd["cmd_doc"]:
        ctx = item.strip('  ')

        if ctx.startswith('.'):
            cmd_args_descr.append(f'<{ctx[1:]}>')
            cmd_area = True
        elif cmd_area:
            cmd_args_descr.append(ctx)
        elif not cmd_area:
            cmd_descr.append(ctx)

    if not cmd_descr:
        return None

    with open(DOC_PATH, mode='a', encoding='utf-8') as file:
        file.write(f'### {cmd_usage}\n\n')
        file.write(f'權限：{cmd_auths}\n\n')
        cmd_descr = '\n'.join(cmd_descr)
        file.write(f'描述：{cmd_descr}\n')

        if cmd_args_descr:
            file.write('\n')
            file.write('```markdown\n')
            file.write('\n'.join(cmd_args_descr))
            file.write('\n')
            file.write('```\n\n')
        else:
            file.write('\n')


def traverse_folder(folder_path):
    for filename in os.listdir(folder_path):
        if not filename.endswith('.py'):
            continue

        made_filename_docu_header = False

        with open(f'{folder_path}/{filename}', mode='r', encoding='utf-8') as file:
            ctx = file.read()

        ctx_ast = ast.parse(ctx)

        for base_obj in ctx_ast.body:
            if not isinstance(base_obj, ast.ClassDef):
                continue

            group_name = ''
            group_auths = []
            group_aliases = []

            for class_obj in base_obj.body:
                if not isinstance(class_obj, ast.AsyncFunctionDef):
                    continue

                cmd_name = ''
                cmd_auths = []
                cmd_aliases = []
                cmd_args = []
                cmd_doc = ''

                decors = class_obj.decorator_list

                is_group = False
                is_command = False
                for decor in decors:
                    if not isinstance(decor, ast.Call):
                        continue

                    attr_obj: ast.Attribute = decor.func

                    if attr_obj.attr == 'group':
                        is_group = True

                    if attr_obj.attr == 'command':
                        is_command = True
                        break

                for decor in decors:
                    if not isinstance(decor, ast.Call):
                        continue

                    attr_obj: ast.Attribute = decor.func

                    # search aliases
                    keywords = decor.keywords
                    for keyword in keywords:
                        decor_type = keyword.arg
                        if decor_type != 'aliases':
                            continue

                        value: ast.List = keyword.value
                        elts = value.elts
                        for elt in elts:
                            if not isinstance(elt, ast.Constant):
                                continue

                            if is_group:
                                group_aliases = elt.value
                            else:
                                cmd_aliases = elt.value

                    # search auths
                    if attr_obj.attr == 'has_any_role':
                        args = decor.args
                        for arg in args:
                            if not isinstance(arg, ast.Constant):
                                continue

                            if is_group:
                                group_auths.append(arg.value)
                            else:
                                cmd_auths.append(arg.value)

                # get group name
                if is_group:
                    group_name = class_obj.name
                    continue  # group has no need to find a parent
                elif is_command:
                    cmd_name = class_obj.name
                elif not is_command:
                    continue

                # get arguments
                arguments: ast.arguments = class_obj.args
                args = arguments.args
                for arg in args:
                    if not isinstance(arg, ast.arg):
                        continue

                    arg_name: str = arg.arg
                    if arg_name != 'self' and arg_name != 'ctx':
                        name_obj = arg.annotation

                        # if typing is tuple of Union
                        if isinstance(name_obj, ast.Subscript):
                            typing_name = name_obj.value
                            if isinstance(typing_name, ast.Attribute):  # discord.Greedy
                                typing_class_name: ast.Name = typing_name.value
                                typing_class_prefix = typing_class_name.id

                                typing_class_suffix = typing_name.attr

                                typing_prefix = f'{typing_class_prefix}.{typing_class_suffix}'
                            elif isinstance(typing_name, ast.Name):  # Union
                                typing_prefix = typing_name.id

                            typing_tuple = name_obj.slice

                            element_in_tuple = []
                            if isinstance(typing_tuple, ast.Tuple):
                                for elt in typing_tuple.elts:
                                    if isinstance(elt, ast.Attribute):
                                        typing_class_name: ast.Name = elt.value
                                        typing_class_prefix = typing_class_name.id

                                        typing_class_suffix = elt.attr

                                        element_in_tuple.append(
                                            f'{typing_class_prefix}.{typing_class_suffix}'
                                        )
                                    elif isinstance(elt, ast.Name):
                                        typing_class_type = elt.id
                                        element_in_tuple.append(typing_class_type)
                            elif isinstance(typing_tuple, ast.Attribute):
                                typing_class_name: ast.Name = typing_tuple.value
                                typing_class_prefix = typing_class_name.id

                                typing_class_suffix = typing_tuple.attr

                                element_in_tuple.append(
                                    f'{typing_class_prefix}.{typing_class_suffix}'
                                )
                            elif isinstance(typing_tuple, ast.Name):
                                typing_class_type = typing_tuple.id
                                element_in_tuple.append(typing_class_type)

                            if not element_in_tuple:
                                continue

                            typing_union = f'{arg_name}: {typing_prefix}[{", ".join(element_in_tuple)}]'
                            cmd_args.append(typing_union)
                        else:
                            if isinstance(name_obj, ast.Attribute):
                                typing_class_name: ast.Name = name_obj.value
                                typing_class_prefix = typing_class_name.id

                                typing_class_suffix = name_obj.attr

                                cmd_args.append(
                                    f'{arg_name}: {typing_class_prefix}.{typing_class_suffix}'
                                )
                            else:
                                arg_type = name_obj.id
                                cmd_args.append(f'{arg_name}: {arg_type}')

                # get doc
                for func_obj in class_obj.body:
                    if not isinstance(func_obj, ast.Expr):
                        continue

                    const_obj = func_obj.value
                    if not isinstance(const_obj, ast.Constant):
                        continue

                    cmd_doc = const_obj.value
                    break

                has_parent = False
                # check if this cmd has a parent
                for decor in decors:
                    if not isinstance(decor, ast.Call):
                        continue

                    attr_obj: ast.Attribute = decor.func
                    name_obj: ast.Name = attr_obj.value

                    if name_obj.id == group_name:
                        has_parent = True

                # create documentation
                cmd_info = {
                    "has_parent": has_parent,
                    "group_name": group_name,
                    "group_auths": group_auths,
                    "group_aliases": group_aliases,
                    "cmd_name": cmd_name,
                    "cmd_auths": cmd_auths,
                    "cmd_aliases": cmd_aliases,
                    "cmd_args": cmd_args,
                    "cmd_doc": cmd_doc
                }
                if not made_filename_docu_header:
                    make_md_header(filename)
                    made_filename_docu_header = True

                insert_docu(cmd_info)


with open(DOC_PATH, mode='a', encoding='utf-8') as file:
    file.write(f'# SQCS_bot command list\n\n')
    file.write(f'Bot version: {VERSION}\n\n')
    file.write('此文件為由程式自動生成的，如果有使用上的疑慮請直接詢問總召。\n\n')

traverse_folder(COGS_PATH)

for filename in os.listdir(COGS_PATH):
    if filename.endswith('.py'):
        pass
    elif '__' in filename:
        pass
    else:
        traverse_folder(f'{COGS_PATH}/{filename}')
