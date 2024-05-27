from datetime import datetime
import os
import re
import tkinter as tk
from tkinter import filedialog
from bs4 import BeautifulSoup

def open_file_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    # Open file dialog and get the selected file
    file_path = filedialog.askopenfilename()
    
    def extract_classes(css_content):
        class_pattern = r'\.([^\s\d{][^\s{]+)'  # Regular expression pattern
        class_names = re.findall(class_pattern, css_content)
        return class_names

    # Read the bootstrap.css file content
    with open("CSSFormatter/bootstrap.css", "r") as css_file:
        bootstrap_css_content = css_file.read()

    bootstrap_class_names = extract_classes(bootstrap_css_content)

    if file_path:
        found_styles_by_selector = {}  # Dictionary to store styles for each selector (class or ID)
        found_ids = set()  # Set to store unique IDs found in the HTML

        with open(file_path, 'r') as file:
            html_content = file.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            # Find all HTML elements that have a 'style' attribute
            elements_with_style = soup.find_all(style=True)
            for element in elements_with_style:
                # Extract and parse the 'style' attribute
                styles = element['style'].split(';')
                for style in styles:
                    if ':' in style:
                        property_name, value = style.split(':', 1)
                        class_list = element.get('class', [])
                        id_name = element.get('id', None)
                        
                        # If the element has a class, use it as the selector
                        if class_list:
                            for class_name in class_list:
                                if class_name not in bootstrap_class_names:  # Exclude classes from bootstrap.css
                                    if class_name not in found_styles_by_selector:
                                        found_styles_by_selector[class_name] = set()
                                    found_styles_by_selector[class_name].add(f"{property_name.strip()}: {value.strip()};")
                        
                        # If the element has an ID, store it
                        if id_name:
                            found_ids.add(id_name)
                            if id_name not in found_styles_by_selector:
                                found_styles_by_selector[id_name] = set()
                            found_styles_by_selector[id_name].add(f"{property_name.strip()}: {value.strip()};")
        
        for element in soup.find_all(style=True):
            del element['style']

        with open(file_path, 'w') as file:
            file.write(soup.prettify())
            
        # CSS Creation    
        css_content = f"/* CSS file for {os.path.basename(file_path)} */\n /* Generated on {datetime.now().strftime("%Y-%m-%d")} */\n\n"
        for selector, styles in found_styles_by_selector.items():
            # Prefix with '.' for classes and '#' for IDs
            selector_prefix = "." if selector not in found_ids else "#"
            css_content += f"{selector_prefix}{selector} {{\n"
            for style in styles:
                css_content += f"    {style}\n"
            css_content += "}\n\n"

        with open("test.css", "w") as css_file: 
            css_file.write(css_content)

open_file_dialog()
print("\nCompleted!\n")
