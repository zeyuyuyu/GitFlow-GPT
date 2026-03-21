import os
from typing import Dict, List
import openai
from git import Repo

class GitFlowGPT:
    def __init__(self, repo_path: str, openai_key: str):
        self.repo = Repo(repo_path)
        openai.api_key = openai_key

    def get_diff_changes(self) -> str:
        """Get git diff of staged changes"""
        return self.repo.git.diff('--cached')

    def generate_pr_description(self, diff: str) -> Dict[str, str]:
        """Generate PR description using GPT"""
        prompt = f"""Based on the following git diff, generate a clear and detailed pull request description.
Include:
1. A concise title
2. Summary of changes
3. Technical implementation details
4. Testing considerations

Git diff:
{diff}
"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are a helpful AI that generates clear and professional pull request descriptions."
            }, {
                "role": "user",
                "content": prompt
            }]
        )

        description = response.choices[0].message.content
        
        # Parse response into sections
        sections = description.split('\n\n')
        return {
            'title': sections[0].strip(),
            'description': '\n\n'.join(sections[1:]).strip()
        }

    def create_pr_with_description(self, base_branch: str = 'main') -> None:
        """Create a PR with AI-generated description"""
        # Get current branch
        current = self.repo.active_branch.name
        
        # Get diff of staged changes
        diff = self.get_diff_changes()
        if not diff:
            raise ValueError("No staged changes found")

        # Generate PR description
        pr_content = self.generate_pr_description(diff)

        # Print results (in real implementation, would use GitHub API to create PR)
        print(f"\nGenerated Pull Request Content:")
        print(f"\nTitle: {pr_content['title']}")
        print(f"\nDescription:\n{pr_content['description']}")

def main():
    # Initialize with environment variables
    repo_path = os.getenv('REPO_PATH', '.')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    gitflow = GitFlowGPT(repo_path, openai_key)
    gitflow.create_pr_with_description()

if __name__ == '__main__':
    main()
