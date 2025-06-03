import os
import shutil

import chevron


class Template:

    def __init__(self, path):
        with open(path, 'r', encoding="UTF-8") as f:
            self.template = f.read()
        self.context = {}
        self.partials = {}
        self.path, self.filename = os.path.split(path)

    def set_context(self, raw_context):
        if isinstance(raw_context, dict) and "data" in raw_context and "partials" in raw_context:
            self.context = raw_context["data"]
            self.partials = raw_context["partials"]
            self.load_partials_from_mapping()
        else:
            self.context = raw_context
        

    def set(self, key, value):
        self.context[key] = value

    def set_partials(self, partials):
        self.partials = partials

    def inject_dynamic_lambdas_with_mapping_and_files(self):
        for doc in self.context.get("documents", []):
            title = doc.get("title", "")

            section = title
            print("Doc: " + str(doc) + "\n Section-Name: " + section + "\nPartials: " + str(self.partials))

            def make_lambda(doc_context, section_name, partial_templates):
                return lambda text, render: chevron.render("{{>" + section_name + "}}", doc_context, partials_dict=partial_templates)

            doc["dynamic_section"] = make_lambda(doc, section, self.partials)
        return self.context

    def load_partials_from_mapping(self):
        for key, partial_name in self.partials.items():
            file_path = os.path.join(self.path, f"{partial_name}.mustache")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding="utf-8") as f:
                    self.partials[key] = f.read()
            else:
                print(f"Warning: Partial file {file_path} not found.")

    def content(self):
        return chevron.render(self.template, self.context, partials_dict=self.partials)

