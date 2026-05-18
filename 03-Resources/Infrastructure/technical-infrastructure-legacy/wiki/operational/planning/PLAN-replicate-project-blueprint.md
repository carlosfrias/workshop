# PLAN: Replicate Project Blueprint Instance

**Created:** 2026-05-03  
**Priority:** 🟢 Low  
**Estimated Effort:** 4-6 hours  
**Domain:** project-templates / site-generation  

---

## Objective

Build a site from templates to replicate a project-blueprint instance, enabling rapid deployment of standardized project structures.

---

## Phase 1: Template Inventory (1-2 hours)

### Tasks
1. **Locate existing project-blueprint**
   - Search workspace for `project-blueprint`, `blueprint`, `template` directories
   - Identify canonical source (Git repo, local directory, cloud storage)
   - Document version and last modification date

2. **Inventory template components**
   - Directory structure (folders, subfolders)
   - Configuration files (`.env`, `config.json`, `settings.yml`)
   - Code templates (`.py`, `.js`, `.md` files)
   - Documentation templates (`README.md`, `CONTRIBUTING.md`)
   - CI/CD configurations (`.github/workflows/`, `.gitlab-ci.yml`)

3. **Identify variable vs. static content**
   - Static: Boilerplate, standard configurations
   - Variable: Project name, description, version, author
   - Conditional: Feature flags, optional modules

### Deliverables
- [ ] Template inventory spreadsheet
- [ ] Directory tree diagram
- [ ] Variable identification document

### Success Criteria
- Complete understanding of blueprint structure
- All variables identified for substitution

---

## Phase 2: Template Extraction (1-2 hours)

### Tasks
1. **Extract template structure**
   - Copy blueprint to template directory
   - Remove project-specific content
   - Replace variables with placeholders:
     - `{{PROJECT_NAME}}`
     - `{{DESCRIPTION}}`
     - `{{VERSION}}`
     - `{{AUTHOR}}`
     - `{{DATE}}`

2. **Create templating system**
   - Option A: Simple string replacement (Python `str.replace()`)
   - Option B: Jinja2 templates (more powerful)
   - Option C: Cookiecutter (standardized template system)

3. **Build configuration file**
   ```yaml
   # template-config.yml
   project:
     name: "My Project"
     description: "Project description"
     version: "0.1.0"
     author: "Your Name"
   structure:
     include_tests: true
     include_docs: true
     ci_platform: "github"  # github, gitlab, none
   ```

### Deliverables
- [ ] Extracted template directory
- [ ] Placeholder substitution system
- [ ] Configuration file template

### Success Criteria
- Template can generate multiple project instances
- No hardcoded project-specific values remain

---

## Phase 3: Site Generation Workflow (2-3 hours)

### Tasks
1. **Build generation script**
   ```python
   # generate_project.py
   import os, shutil
   from jinja2 import Environment, FileSystemLoader
   
   def generate_project(config_file, output_dir):
       # Load config
       # Copy template structure
       # Substitute variables
       # Write output files
       pass
   ```

2. **Implement interactive prompts**
   ```bash
   $ python generate_project.py
   Project name: My New Project
   Description: Automated project generation
   Version: 0.1.0
   Author: Your Name
   Include tests? [y/N]: y
   Include docs? [Y/n]: y
   CI platform? [github/gitlab/none]: github
   
   ✓ Project created in ./my-new-project/
   ```

3. **Add post-generation hooks**
   - Initialize Git repository
   - Install dependencies (`pip install -r requirements.txt`)
   - Run initial tests
   - Open in editor/IDE

4. **Create validation checks**
   - Verify all placeholders replaced
   - Check file permissions
   - Validate generated configuration
   - Test critical paths

### Deliverables
- [ ] Project generation script
- [ ] Interactive CLI interface
- [ ] Post-generation automation
- [ ] Validation checks

### Success Criteria
- New project generated in <30 seconds
- All files properly configured
- No placeholder strings remain

---

## Phase 4: Customization Points (1-2 hours)

### Tasks
1. **Define extension points**
   - Module addition hooks
   - Custom configuration overrides
   - Plugin architecture (if needed)
   - Theme/styling variations

2. **Create customization documentation**
   - How to add new modules
   - How to modify existing templates
   - How to create custom configurations
   - Best practices for extensions

3. **Build example customizations**
   - Example 1: Add Docker support
   - Example 2: Add pre-commit hooks
   - Example 3: Custom CI/CD pipeline
   - Example 4: Alternative project structure

### Deliverables
- [ ] Extension points documentation
- [ ] Customization guide
- [ ] 3-4 example customizations

### Success Criteria
- Users can customize without modifying core template
- Examples demonstrate common use cases

---

## Phase 5: Deployment Options (1 hour)

### Tasks
1. **Local deployment**
   - Script runs from local directory
   - Templates stored in `~/.project-templates/`
   - Output to current directory or specified path

2. **Git-based deployment**
   - Template repo on GitHub/GitLab
   - Clone template, run generation script
   - Version control for template updates

3. **Package-based deployment**
   - Publish as PyPI package (`pip install project-blueprint`)
   - CLI command: `blueprint new my-project`
   - Automatic updates via pip

4. **Container deployment**
   - Docker image with generation tools
   - Consistent environment across systems
   - Useful for CI/CD integration

### Deliverables
- [ ] Deployment documentation for each option
- [ ] Installation scripts
- [ ] Version update mechanism

### Success Criteria
- At least 2 deployment methods functional
- Clear instructions for end users

---

## Tools & Technologies

### Templating
- Jinja2 (Python)
- Cookiecutter (standardized)
- Mustache (language-agnostic)

### Project Generation
- Python scripts
- Shell scripts (bash)
- Node.js (if JavaScript-focused)

### Distribution
- PyPI (Python packages)
- npm (Node.js packages)
- Git repositories
- Docker images

---

## Success Metrics

- [ ] Template generates complete project in <30 seconds
- [ ] Zero placeholder strings in generated output
- [ ] 5+ projects successfully generated from template
- [ ] Customization documentation clear and actionable
- [ ] At least 2 deployment methods functional

---

## Notes

- Consider using existing tools (Cookiecutter) before building custom solution
- Template maintenance is ongoing — plan for updates
- Version control for templates enables rollback if issues arise
- Community contributions can improve template over time

---

**END OF PLAN**
