# Release Checklist

Use this checklist for every release.

## Before release

- [ ] `git pull --rebase origin main`
- [ ] Update `vett/__init__.py` version
- [ ] Update `CHANGELOG.md`
- [ ] Verify install and scan:
  - [ ] `pip install -e .`
  - [ ] `python -m vett.cli version`
  - [ ] `python -m vett.cli scan . --no-ai`
- [ ] Commit: `chore(release): vX.Y.Z`
- [ ] Push to `main`

## Publish

- [ ] Create GitHub release/tag: `vX.Y.Z`
- [ ] Confirm workflow success: `Publish to PyPI`
- [ ] Verify package on PyPI
- [ ] Verify `pip install -U vett` installs new version

## After release

- [ ] Create new `Unreleased` section in `CHANGELOG.md` (if needed)
- [ ] Announce release notes
