from pathlib import Path
from vision_studio.core import audit_folder, make_sample_images, write_html


def test_sample_audit_finds_duplicate(tmp_path: Path):
    folder = tmp_path / 'images'
    make_sample_images(folder, count=4)
    result = audit_folder(folder)
    assert result['images'] == 5
    assert result['flagged'] >= 1
    assert any('exact_duplicate' in row['flags'] for row in result['records'])


def test_html_report_is_written(tmp_path: Path):
    folder = tmp_path / 'images'
    make_sample_images(folder, count=2)
    output = tmp_path / 'report.html'
    write_html(audit_folder(folder), output)
    assert output.exists()
    assert 'Vision Dataset Studio' in output.read_text()
