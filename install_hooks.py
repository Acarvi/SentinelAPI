import os
import shutil
import stat

def install_hooks():
    """
    Installs the SentinelAPI pre-push hook into sibling git repositories.
    """
    scripts_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hook_source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "git-hooks", "pre-push")

    if not os.path.exists(hook_source):
        print(f"❌ Error: Hook source not found at {hook_source}")
        return

    # Scan for git repositories in the scripts root
    projects_to_protect = [
        "EconomikaNoticias",
        "CentralAIService",
        "perplexity_scraper",
        "CentralPublishingHub"
    ]

    for project in projects_to_protect:
        project_path = os.path.join(scripts_root, project)
        git_hooks_dir = os.path.join(project_path, ".git", "hooks")
        
        if os.path.exists(git_hooks_dir):
            hook_dest = os.path.join(git_hooks_dir, "pre-push")
            print(f"[PACK] Installing hook in {project}...")
            
            try:
                # Copy the hook file
                shutil.copy2(hook_source, hook_dest)
                
                # Make it executable (critical for Unix-like systems, including Git Bash)
                st = os.stat(hook_dest)
                os.chmod(hook_dest, st.st_mode | stat.S_IEXEC)
                
                print(f"   [OK] Installed at {hook_dest}")
            except Exception as e:
                print(f"   [ERROR] Failed to install in {project}: {e}")
        else:
            print(f"[SKIP] Skipping {project}: .git/hooks directory not found.")

if __name__ == "__main__":
    install_hooks()
