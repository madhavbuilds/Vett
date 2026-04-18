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

### One-time: PyPI trusted publisher (if `Publish to PyPI` fails with `invalid-publisher`)

The workflow uses [trusted publishing](https://docs.pypi.org/trusted-publishers/adding-a-publisher/) (OIDC), not a `PYPI_API_TOKEN` secret. Configure PyPI once:

1. Open [PyPI → vett → Publishing settings](https://pypi.org/manage/project/vett/settings/publishing/).
2. Under **GitHub**, add a trusted publisher with values that **exactly** match what GitHub sends (case-sensitive):
   - **PyPI project name:** `vett`
   - **Owner:** `madhavbuilds`
   - **Repository name:** `Vett` (capital **V**, as on GitHub)
   - **Workflow filename:** `publish-pypi.yml`
   - **Environment name:** leave **blank** (this repo’s workflow does not use a GitHub Environment).
3. Save, then in GitHub Actions open the failed run and click **Re-run failed jobs** (no new tag required).

### Every release

- [ ] Create GitHub release/tag: `vX.Y.Z`
- [ ] Confirm workflow success: `Publish to PyPI`
- [ ] Verify package on PyPI
- [ ] Verify `pip install -U vett` installs new version

## After release

- [ ] Create new `Unreleased` section in `CHANGELOG.md` (if needed)
- [ ] Announce release notes
