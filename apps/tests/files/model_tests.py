from uuid import UUID

import pytest


@pytest.mark.django_db
def test_file_instance(data_file):
    assert isinstance(data_file.id, UUID)
    assert data_file.uploader.email == 'doctor@test.com'
