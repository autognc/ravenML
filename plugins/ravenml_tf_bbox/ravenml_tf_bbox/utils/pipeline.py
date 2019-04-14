import os
import yaml


pipeline_path = os.path.join('pipeline_configurable.config')
base_dir = "replaced/path"

model_folder = '/Users/nihaldhamani/Desktop'


with open('config_template.yml', 'r') as f:
    try:
        defaults = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        print(exc)

with open(pipeline_path) as template:
    pipeline_contents = template.read()

if base_dir.endswith('/') or base_dir.endswith(r"\\"):
    pipeline_contents = pipeline_contents.replace('<replace_path>', base_dir)
else:
    if os.name == 'nt':
        pipeline_contents = pipeline_contents.replace('<replace_path>', base_dir + r"\\")
    else:
        pipeline_contents = pipeline_contents.replace('<replace_path>', base_dir + '/')

for choice in defaults:

    ans = input("would you like to change " + choice + " (y/n): ")
    if ans == 'y' or ans == 'Y':
        change = input("default=" + str(defaults[choice]).lower() + " change to: ")
        defaults[choice] = change
    
    formatted = '<replace_' + choice + '>'
    pipeline_contents = pipeline_contents.replace(formatted, str(defaults[choice]))


pipeline_path = os.path.join(model_folder, 'pipeline.config')
with open(pipeline_path, 'w') as file:
    file.write(pipeline_contents)
print('Created pipeline.config file inside models/model/')
