
import pytest
from bot.utils import romanize_korean

def test_romanize_korean():
    assert romanize_korean('학교') == 'hakgyo'
    assert romanize_korean('사랑') == 'sarang'
