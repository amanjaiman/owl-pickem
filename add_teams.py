import os

directory = r'C:\Users\amanj\Documents\RandomProjects\owlpickem\mysite\ow_logos'

for filename in os.listdir(directory):
    name = filename.split("-")[1]
    name = name.split("_logo")[0]
    name = ' '.join(name.split("_"))

    print(os.path.join('uploads', filename))