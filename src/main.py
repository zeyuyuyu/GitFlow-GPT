import os
import subprocess
from typing import List, Dict
import openai
from git import Repo

class GitFlowGPT:
    def __init__(self, repo_path: str, openai_key: str):
        self.repo = Repo(repo_path)
        self.git = self.repo.git
        openai.api_key = openai_key

    def analyze_changes(self) -> Dict[str, str]:
        """Analyze uncommitted changes using GPT to suggest branch naming and PR description"""
        diff = self.git.diff()
        
        prompt = f"Analyze these git changes and suggest:
1. A semantic branch name (feat/fix/refactor)
2. A detailed PR description

Changes:
{diff}"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse GPT response
        content = response.choices[0].message.content
        lines = content.split('\n')
        branch_name = lines[0].strip()
        pr_description = '\n'.join(lines[1:]).strip()

        return {
            "branch_name": branch_name,
            "pr_description": pr_description
        }

    def create_feature_branch(self, branch_name: str) -> None:
        """Create and checkout a new feature branch"""
        current = self.repo.active_branch.name
        if current != 'main' and current != 'master':
            raise ValueError(f"Must be on main/master branch, currently on {current}")

        self.git.checkout('HEAD', b=branch_name)

    def create_pull_request(self, title: str, body: str) -> None:
        """Create a pull request using GitHub CLI"""
        try:
            subprocess.run([
                'gh', 'pr', 'create',
                '--title', title,
                '--body', body
            ], check=True)
        except subprocess.CalledProcessError:
            print("Error: Ensure GitHub CLI is installed and authenticated")

    def smart_commit(self) -> None:
        """Analyze changes and create a semantically named branch with PR"""
        # Analyze current changes
        analysis = self.analyze_changes()
        branch_name = analysis['branch_name']
        pr_description = analysis['pr_description']

        # Create feature branch
        self.create_feature_branch(branch_name)

        # Stage and commit changes
        self.git.add('.')
        self.git.commit('-m', f"{branch_name}: Automated commit")

        # Push branch and create PR
        self.git.push('--set-upstream', 'origin', branch_name)
        self.create_pull_request(
            title=branch_name,
            body=pr_description
        )

def main():
    repo_path = os.getenv('REPO_PATH', '.')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    gitflow = GitFlowGPT(repo_path, openai_key)
    gitflow.smart_commit()

if __name__ == '__main__':
    main()