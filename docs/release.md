# Release checklist

1. Update `CHANGELOG.md` and the version tag plan.
2. Run `python scripts/validate_repo.py` and `python -m unittest discover -s tests -p "test_*.py"`.
3. Run the official `quick_validate.py` against `skills/agy-review-loop`.
4. Review the complete diff for secrets, unrelated files, and stale installation paths.
5. Confirm README installation instructions use the intended public owner/repository.
6. Create a signed or annotated version tag only after the user explicitly approves publishing.
7. Publish release notes after CI is green.
