# To-do

- [ ] Customize bot prefix (need db)
- [ ] Anonymous comment (need db)
```markdown
log::Permanent:
ano_event = {
	"<ano_id>": tuple = (commit_user_id, timestamp)
}

log::Temporary(For permission, delete after permitted):
ano_apply_event = {
	msg.content: str,
	msg.ano_id: int(<year><month><day><hour><minute>),
	msg.commit_user_id: int
}
```

- [ ] Anonymous poll event (need db)
```markdown
log::Temporary(Delete after ended):
poll_event = {
	"_id": str(poll_id),
	"name": qns,
	"choices_count": choices_dict,
	"answered_user_id": []
}
```