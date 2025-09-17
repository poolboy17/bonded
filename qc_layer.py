import textstat, re

def qc_checks(text, title, meta):
    errs = []
    if len(text.split()) < 800:
        errs.append(f"Wordcount {len(text.split())}<800")
    if not 45 <= len(title) <= 70:
        errs.append(f"Title len {len(title)}")
    if textstat.flesch_reading_ease(text) < 50:
        errs.append("Low readability")
    if len(re.findall(r"^##", text, flags=re.M)) < 3:
        errs.append("Few H2s")
    focus = meta.get('focus_keyword')
    if focus and focus.lower() not in text.lower():
        errs.append("Missing focus keyword")
    if '## FAQ' not in text:
        errs.append("Missing FAQ")
    return errs
