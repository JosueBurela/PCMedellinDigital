import re

def migrate_template(file_path, icon, title, is_capacitaciones=False):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Find actions in header
    m_actions = re.search(r'<div class="flex items-center gap-1.5 sm:gap-2 shrink-0">(.*?)</div>\s*</header>', text, re.DOTALL)
    if not m_actions:
        m_actions = re.search(r'<div class="flex items-center gap-2 shrink-0">(.*?)</div>\s*</header>', text, re.DOTALL)
    top_actions = m_actions.group(1).strip() if m_actions else ''

    # Find main content
    m_main = re.search(r'<main.*?>(.*?)</main>', text, re.DOTALL)
    main_content = m_main.group(1).strip() if m_main else ''

    # Build new html
    new_html = f"""{{% extends 'portal/base_admin.html' %}}
{{% load static %}}

{{% block page_title %}}
    <i data-lucide="{icon}" class="w-5 h-5 text-medellinOro"></i>
    {title}
{{% endblock %}}

{{% block top_actions %}}
{top_actions}
{{% endblock %}}

{{% block content %}}
<div class="space-y-6">
{main_content}
</div>
{{% endblock %}}
"""

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

migrate_template('portal/templates/portal/vehiculos_admin_dashboard.html', 'ambulance', 'Control de Flotilla')
migrate_template('portal/templates/portal/capacitacion_admin_dashboard.html', 'graduation-cap', 'Cursos y Constancias', True)
print("Migration done")
