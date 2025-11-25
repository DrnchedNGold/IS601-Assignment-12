import pytest
from app.models.calculation import Addition, Subtraction, Multiplication, Division

def test_addition_invalid_inputs():
    add = Addition(inputs="notalist")
    with pytest.raises(ValueError):
        add.get_result()
    add = Addition(inputs=[1])
    with pytest.raises(ValueError):
        add.get_result()

def test_subtraction_invalid_inputs():
    sub = Subtraction(inputs="notalist")
    with pytest.raises(ValueError):
        sub.get_result()
    sub = Subtraction(inputs=[1])
    with pytest.raises(ValueError):
        sub.get_result()

def test_multiplication_invalid_inputs():
    mul = Multiplication(inputs="notalist")
    with pytest.raises(ValueError):
        mul.get_result()
    mul = Multiplication(inputs=[1])
    with pytest.raises(ValueError):
        mul.get_result()

def test_division_invalid_inputs():
    div = Division(inputs="notalist")
    with pytest.raises(ValueError):
        div.get_result()
    div = Division(inputs=[1])
    with pytest.raises(ValueError):
        div.get_result()
    div = Division(inputs=[1, 0])
    with pytest.raises(ValueError):
        div.get_result()
