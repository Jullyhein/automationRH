import pytest
from unittest.mock import patch, MagicMock

from graphutils import (
    get_access_token,
    get_aniversariantes_com_imagem,
    formatar_nome_curto
)

# --------------------------
# Teste: get_access_token
# --------------------------
@patch("graphutils.requests.post")
def test_get_access_token(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "fake_token"}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    token = get_access_token()
    assert token == "fake_token"
    mock_post.assert_called_once()

# --------------------------
# Teste: formatar_nome_curto
# --------------------------
@pytest.mark.parametrize("input_nome, expected", [
    ("João da Silva", "João Silva"),
    ("Maria de Souza", "Maria Souza"),
    ("Carlos dos Santos Oliveira", "Carlos Oliveira"),
    ("Ana", "Ana"),
    ("  Pedro   de Alcântara   ", "Pedro Alcântara"),
])
def test_formatar_nome_curto(input_nome, expected):
    assert formatar_nome_curto(input_nome) == expected

# --------------------------
# Teste: get_aniversariantes_com_imagem
# --------------------------
@patch("graphutils.buscar_aniversariantes_hoje")
@patch("graphutils.listar_conteudo_pasta")
@patch("graphutils.get_active_employees")
def test_get_aniversariantes_com_imagem(mock_employees, mock_imagens, mock_buscar):
    mock_buscar.return_value = ["12345678900"]
    mock_imagens.return_value = {"12345678900": "base64imagemfake"}
    mock_employees.return_value = [
        {"employeeCpf": "12345678900", "name": "Maria dos Anjos"}
    ]

    result = get_aniversariantes_com_imagem("fake_token")
    assert len(result) == 1
    aniversariante = result[0]
    assert aniversariante["name"] == "Maria Anjos"
    assert aniversariante["cpf"] == "12345678900"
    assert aniversariante["tem_imagem"] is True
    assert aniversariante["metodo"] == "inline"
    assert aniversariante["image_base64"] == "base64imagemfake"

@patch("graphutils.buscar_aniversariantes_hoje")
def test_get_aniversariantes_sem_cpfs(mock_buscar):
    mock_buscar.return_value = []
    result = get_aniversariantes_com_imagem("fake_token")
    assert result == []
