# Модуль для просмотра ВАХ

Настраиваемый PyQt-виджет для отображения Вольт-Амперных Характеристик (ВАХ). Виджет умеет выводить несколько ВАХ на график и при необходимости обновлять их.

# Установка

Установка возможна только на python версии 3.6!

```bash
python3.6 -m pip install ivviewer
```

# Проверка установки

```bash
python -m ivviewer 	# при успешной установке создаст окно с графиком 
```

# Пример использования

```python
	app = QApplication(sys.argv)
	window = ivviewer.Viewer()
	window.setFixedSize(600, 600)
	window.plot.set_scale(14.0, 28.0)

	x_test = [-2.5, 0, 2.5]
        y_test = [-0.005, 0, 0.005]
        test_curve = window.plot.add_curve()
        test_curve.set_curve(Curve(x_test, y_test))

        x_ref = [-2.5, 0, 2.5]
        y_ref = [-0.003, 0, 0.003]
        reference_curve = window.plot.add_curve()
        reference_curve.set_curve(Curve(x_ref, y_ref))

        window.show()
        app.exec()
```
