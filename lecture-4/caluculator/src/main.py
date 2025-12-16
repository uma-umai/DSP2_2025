import flet as ft
import math

class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text


class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.Colors.WHITE24
        self.color = ft.Colors.WHITE


class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.ORANGE
        self.color = ft.Colors.WHITE


class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.BLUE_GREY_400
        self.color = ft.Colors.WHITE


class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()
        self.angle_unit = "DEG"

        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=20)
        self.width = 350
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="DEG/RAD", button_clicked=self.button_clicked),
                        ExtraActionButton(text="sin", button_clicked=self.button_clicked),
                        ExtraActionButton(text="cos", button_clicked=self.button_clicked),
                        ExtraActionButton(text="tan", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                        ExtraActionButton(text="+/-", button_clicked=self.button_clicked),
                        ExtraActionButton(text="π", button_clicked=self.button_clicked),
                        ExtraActionButton(text="x^y", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="0", expand=2, button_clicked=self.button_clicked),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
            ]
        )

    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data}")
        
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()
            self.update()
            return
            
        try:
            current_value = float(self.result.value)
        except ValueError:
            current_value = 0.0

        
        if data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            if self.result.value == "0" or self.new_operand == True:
                self.result.value = data
                self.new_operand = False
            elif data == "." and "." in self.result.value:
                pass
            else:
                self.result.value = self.result.value + data
        
        elif data in ("+", "-", "*", "/", "x^y"):
            self.result.value = self.calculate(self.operand1, current_value, self.operator)
            self.operator = data
            if self.result.value == "Error":
                self.operand1 = 0
            else:
                self.operand1 = float(self.result.value)
            self.new_operand = True

        elif data in ("="):
            self.result.value = self.calculate(self.operand1, current_value, self.operator)
            self.reset()
        
        elif data == "π":
            self.result.value = self.format_number(math.pi)
            self.new_operand = True
            
        elif data in ("sin", "cos", "tan"):
            try:
                if self.angle_unit == "DEG":
                    value_rad = math.radians(current_value)
                else:
                    value_rad = current_value

                if data == "sin":
                    result_value = math.sin(value_rad)
                elif data == "cos":
                    result_value = math.cos(value_rad)
                elif data == "tan":
                    if self.angle_unit == "DEG" and abs(current_value) % 180 == 90:
                         result_value = float('inf')
                    else:
                        result_value = math.tan(value_rad)

                self.result.value = self.format_number(result_value)
                self.new_operand = True
                
            except ValueError:
                self.result.value = "Error"
                self.reset()
            except Exception:
                self.result.value = "Error"
                self.reset()

        elif data in ("%"):
            self.result.value = self.format_number(current_value / 100)
            self.reset()

        elif data in ("+/-"):
            self.result.value = self.format_number(-current_value)
            
        elif data == "DEG/RAD":
            self.angle_unit = "RAD" if self.angle_unit == "DEG" else "DEG"
            print(f"Angle unit switched to: {self.angle_unit}")

        self.update()

    def format_number(self, num):
        if abs(num) < 1e-10:
            return 0
            
        if num % 1 == 0:
            return int(num)
        else:
            return num

    def calculate(self, operand1, operand2, operator):

        if operator == "+":
            return self.format_number(operand1 + operand2)

        elif operator == "-":
            return self.format_number(operand1 - operand2)

        elif operator == "*":
            return self.format_number(operand1 * operand2)

        elif operator == "/":
            if operand2 == 0:
                return "Error"
            else:
                return self.format_number(operand1 / operand2)
        
        elif operator == "x^y":
            try:
                return self.format_number(math.pow(operand1, operand2))
            except OverflowError:
                return "Error"
            except Exception:
                return "Error"

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True


def main(page: ft.Page):
    page.title = "Scientific Calculator"
    calc = CalculatorApp()
    page.add(calc)


ft.app(main)