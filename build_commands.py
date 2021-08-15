import os
import re

cogs_path = './bot/cogs'

doc_path = './command_list.md'

prefix = '+'

if os.path.isfile(doc_path):
    os.remove(doc_path)

def get_name(name):
    return name.strip(' ').strip('(').strip(')')

def make_md_header(filename):
    with open(doc_path, mode='a', encoding='utf-8') as file:
        file.write(f'## {filename}\n\n')

def make_docu(group_auth, group_name, cmd_auth, cmd_name, cmd_args, cmd_comment):
    with open(doc_path, mode='a', encoding='utf-8') as file:
        if not cmd_args:
            cmd_args = None
        else:
            cmd_args = get_name(cmd_args).split(', ')[2:]
            clear_cmd_args = []
            for arg in cmd_args:
                new_arg = ''
                break_point = 0
                breaking = False
                for index, string in enumerate(arg):
                    if not breaking:
                        if string == '=':
                            new_arg += arg[break_point:index]
                            breaking = True
                    elif breaking:
                        if string == ',':
                            break_point = index
                            breaking = False
                if new_arg == '':
                    new_arg = arg
                clear_cmd_args.append(new_arg.strip(' '))
        
        cmd_usage = f'{prefix}'
        if get_name(group_name):
            cmd_usage += f'{get_name(group_name)} {get_name(cmd_name)}'
        else:
            cmd_usage += f'{get_name(cmd_name)}'

        if clear_cmd_args:
            cmd_usage += f' {" ".join(f"<{arg}>" for arg in clear_cmd_args)}'
        
        file.write(f'### {cmd_usage}\n\n')

        descr = []
        args_descr = []
        arg_order = 0

        cmd_area = False
        for item in cmd_comment:
            ctx = item.strip('  ')
            if ctx.startswith('.'):
                args_descr.append(f'<{ctx[1:]}>')
                arg_order += 1
                cmd_area = True
            elif cmd_area:
                args_descr.append(ctx)
            elif not cmd_area:
                descr.append(ctx)

        if cmd_auth == '':
            if group_auth == '':
                cmd_auth = '無'
            else:
                cmd_auth = group_auth
        
        cmd_auth = [get_name(auth).strip('\'') for auth in cmd_auth.split(', ')]
        
        cmd_auth = [f'`{auth}`' for auth in cmd_auth]
        file.write(f'權限：{" ".join(cmd_auth)}\n\n')
        
        descr = "\n".join(descr)
        file.write(f'描述：\n{descr}\n')

        if args_descr:
            file.write('```markdown\n')
            file.write('\n'.join(args_descr))
            file.write('\n')
            file.write('```\n\n')
        else:
            file.write('\n')

def parse_file(cogs_path):
    for filename in os.listdir(cogs_path):
        if filename.endswith('.py'):
            with open(f'{cogs_path}/{filename}', mode='r', encoding='utf-8') as file:
                codes = file.read()
            
            codes = codes.split('\n')

            find = False
            find_start_point = 0

            cur_cmd_auth = ''
            cur_cmd_name = ''
            cur_cmd_args = ''

            cur_cmd_group_auth = ''
            cur_cmd_group_name = ''
            cur_pos = 0

            make_header = False

            while cur_pos < len(codes):
                if "@commands.command" in codes[cur_pos]:
                    for item in codes[cur_pos:]:
                        if not find:
                            if "@commands.has_any_role" in item:
                                cur_cmd_auth = re.findall(r"\(\D+\)", item)[0]
                            elif "async def" in item:
                                cur_cmd_name = re.findall(r"[def]{3}[\D]+\(", item)[0].strip('def ')
                                cur_cmd_args = re.findall(r"\(.+\)", item)[0]
                            elif '"""cmd' in item:
                                find = True
                                cur_pos += 2
                                find_start_point = cur_pos
                                cur_pos += 1
                            elif item == '':
                                break
                            else:
                                cur_pos += 1
                        elif find:
                            for item in codes[cur_pos:]:
                                if '"""' in item:
                                    find = False
                                    cmd_comment = codes[find_start_point + 1:cur_pos]
                                    make_docu(
                                        '',
                                        '',
                                        cur_cmd_auth,
                                        cur_cmd_name,
                                        cur_cmd_args,
                                        cmd_comment
                                    )
                                    
                                    find = False
                                    cur_pos += 1
                                    break
                                else:
                                    cur_pos += 1
                elif "@commands.group" in codes[cur_pos]:
                    if not make_header:
                        make_md_header(filename)
                        make_header = True
                    
                    for item in codes[cur_pos:]:
                        if "@commands.has_any_role" in item:
                            cur_cmd_group_auth = re.findall(r"\(.+\)", item)[0]
                        elif "async def" in item:
                            cur_cmd_group_name = re.findall(r"[def]{3}[\D]+\(", item)[0].strip('def ').strip('(')
                        elif '.command' in item:
                            break

                        cur_pos += 1
                elif f"{cur_cmd_group_name}.command" in codes[cur_pos]:
                    for item in codes[cur_pos:]:
                        if not find:
                            if "@commands.has_any_role" in item:
                                cur_cmd_auth = re.findall(r"\(\D+\)", item)[0]
                            elif "async def" in item:
                                cur_cmd_name = re.findall(r"[def]{3}[\D]+\(", item)[0].strip('def ')
                                cur_cmd_args = re.findall(r"\(.+\)", item)[0]
                            elif '"""cmd' in item:
                                find = True
                                cur_pos += 1
                                find_start_point = cur_pos
                                cur_pos += 1
                            elif item == '':
                                break
                            else:
                                cur_pos += 1
                        elif find:
                            for item in codes[cur_pos:]:
                                if '"""' in item:
                                    find = False
                                    cmd_comment = codes[find_start_point + 1:cur_pos]
                                    make_docu(
                                        cur_cmd_group_auth,
                                        cur_cmd_group_name,
                                        cur_cmd_auth,
                                        cur_cmd_name,
                                        cur_cmd_args,
                                        cmd_comment
                                    )
                                    
                                    find = False
                                    cur_pos += 1
                                    break
                                else:
                                    cur_pos += 1
                else:
                    cur_pos += 1
        elif '__' in filename:
            pass
        else:
            parse_file(f'{cogs_path}/{filename}')

with open(doc_path, mode='a', encoding='utf-8') as file:
        file.write('# SQCS_Bot Command List\n\n')

parse_file(cogs_path)