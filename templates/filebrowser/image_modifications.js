[{% for img_mod in image_modifications %}["{{ img_mod.sysname|escapejs }}","{{ img_mod.title|escapejs }}"]{% if not forloop.last %},{% endif %}{% endfor %}]
