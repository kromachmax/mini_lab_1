import json
import matplotlib
import numexpr as ne
import numpy as np
from functools import partial
from tkinter import *
from tkinter.filedialog import asksaveasfile, askopenfile
from tkinter import messagebox
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

matplotlib.use('TkAgg')

# Класс для хранения текстовых полей
class Entries:
    def __init__(self):
        self.entries_list = []
        self.parent_window = None

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

    # Добавление нового текстового поля
    def add_entry(self, initial_text=""):
        new_entry = Entry(self.parent_window)
        new_entry.icursor(0)
        new_entry.focus()
        new_entry.pack()
        plot_button = self.parent_window.get_button_by_name('plot')
        if plot_button:
            plot_button.pack_forget()
        self.parent_window.add_button('plot', 'Plot', 'plot', hot_key='<Return>')
        self.entries_list.append(new_entry)
        new_entry.insert(0, initial_text)  # Устанавливаем начальный текст

    # Удаление активного текстового поля
    def delete_active_entry(self):
        if self.entries_list:
            active_entry = self.parent_window.focus_get()
            if active_entry in self.entries_list:
                get_func_str = active_entry.get()
                if get_func_str.strip():  # Проверка, что текстовое поле не пустое
                    # Отображаем модальное окно с запросом подтверждения удаления
                    confirm = messagebox.askyesno("Подтверждение удаления", "Вы уверены, что хотите удалить непустое текстовое поле?")
                    if not confirm:
                        return  # Если пользователь отменил удаление, ничего не делаем
                active_entry.pack_forget()
                self.entries_list.remove(active_entry)
                self.parent_window.commands.plot()

        # Удаление последнего текстового поля
    def delete_last_entry(self):
        if self.entries_list:
            last_entry = self.entries_list[-1]  # Получаем последнее текстовое поле
            get_func_str = last_entry.get()
            if get_func_str.strip():  # Проверка, что текстовое поле не пустое
                # Отображаем модальное окно с запросом подтверждения удаления
                confirm = messagebox.askyesno("Подтверждение удаления",
                                              "Вы уверены, что хотите удалить непустое текстовое поле?")
                if not confirm:
                    return  # Если пользователь отменил удаление, ничего не делаем
            last_entry.pack_forget()
            self.entries_list.pop()  # Удаляем последнее текстовое поле
            self.parent_window.commands.plot()

    # Получение текстовых полей как список строк
    def get_entries_as_list(self):
        return [entry.get() for entry in self.entries_list]

# Класс для построения графиков
class Plotter:
    def __init__(self, x_min=-20, x_max=20, dx=0.01):
        self.x_min = x_min
        self.x_max = x_max
        self.dx = dx
        self._last_plotted_list_of_function = None
        self._last_plotted_figure = None
        self.parent_window = None

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

    # Построение графиков функций
    def plot(self, list_of_function, title='Графики функций', x_label='x', y_label='y', need_legend=True):
        fig = plt.figure()

        x = np.arange(self.x_min, self.x_max, self.dx)

        new_funcs = [f if 'x' in f else 'x/x * ({})'.format(f) for f in list_of_function]

        ax = fig.add_subplot(1, 1, 1)
        for func in new_funcs:
            ax.plot(x, ne.evaluate(func), linewidth=1.5)

        fig.suptitle(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        if need_legend:
            plt.legend(list_of_function)
        self._last_plotted_list_of_function = list_of_function
        self._last_plotted_figure = fig
        return fig

# Класс для хранения команд
class Commands:
    class State:
        def __init__(self):
            self.list_of_function = []

        def save_state(self):
            tmp_dict = {'list_of_function': self.list_of_function}
            file_out = asksaveasfile(defaultextension=".json")
            if file_out is not None:
                json.dump(tmp_dict, file_out)
            return self

        def reset_state(self):
            self.list_of_function = []

    def __init__(self):
        self.command_dict = {}
        self.__figure_canvas = None
        self.__navigation_toolbar = None
        self._state = Commands.State()
        self.__empty_entry_counter = 0
        self.parent_window = None

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

    def add_command(self, name, command):
        self.command_dict[name] = command

    def get_command_by_name(self, command_name):
        return self.command_dict[command_name]

    def __forget_canvas(self):
        if self.__figure_canvas is not None:
            self.__figure_canvas.get_tk_widget().pack_forget()

    def __forget_navigation(self):
        if self.__navigation_toolbar is not None:
            self.__navigation_toolbar.pack_forget()

    def plot(self, *args, **kwargs):
        def is_not_blank(s):
            return bool(s and not s.isspace())

        self._state.reset_state()
        list_of_function = []
        for entry in self.parent_window.entries.entries_list:
            get_func_str = entry.get()
            self._state.list_of_function.append(get_func_str)
            if is_not_blank(get_func_str):
                list_of_function.append(get_func_str)
            else:
                if self.__empty_entry_counter == 0:
                    mw = ModalWindow(self.parent_window, title='Пустая строка',
                                     labeltext='Это пример модального окна, '
                                               'возникающий, если ты ввел '
                                               'пустую '
                                               'строку. С этим ничего '
                                               'делать не нужно. '
                                               'Просто нажми OK :)')
                    ok_button = Button(master=mw.top, text='OK', command=mw.cancel)
                    mw.add_button(ok_button)
                    self.__empty_entry_counter = 1
        self.__empty_entry_counter = 0
        figure = self.parent_window.plotter.plot(list_of_function)
        self._state.figure = figure
        self.__forget_canvas()
        self.__figure_canvas = FigureCanvasTkAgg(figure, self.parent_window)
        self.__forget_navigation()
        self.__navigation_toolbar = NavigationToolbar2Tk(self.__figure_canvas, self.parent_window)
        self.__figure_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        plot_button = self.parent_window.get_button_by_name('plot')
        if plot_button:
            plot_button.pack_forget()

    def add_func(self, *args, **kwargs):
        self.__forget_canvas()
        self.__forget_navigation()
        self.parent_window.entries.add_entry()

    def save_as(self):
        self._state.save_state()
        return self

    # Загрузка сохраненной сессии из файла JSON
    def load_session(self):
        file_in = askopenfile(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_in:
            try:
                data = json.load(file_in)
                if 'list_of_function' in data:
                    list_of_function = data['list_of_function']
                    for func_str in list_of_function:
                        self.parent_window.entries.add_entry(func_str)
                    self.parent_window.commands.plot()
            except json.JSONDecodeError:
                messagebox.showerror("Ошибка", "Не удалось загрузить сессию из файла")

# Класс для хранения кнопок
class Buttons:
    def __init__(self):
        self.buttons = {}
        self.parent_window = None

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

    def add_button(self, name, text, command):
        new_button = Button(master=self.parent_window, text=text, command=command)
        self.buttons[name] = new_button
        return new_button

    def delete_button(self, name):
        button = self.buttons.get(name)
        if button:
            button.pack_forget()

# Класс для генерации модальных окон
class ModalWindow:
    def __init__(self, parent, title, labeltext=''):
        self.buttons = []
        self.top = Toplevel(parent)
        self.top.transient(parent)
        self.top.grab_set()
        if len(title) > 0:
            self.top.title(title)
        if len(labeltext) == 0:
            labeltext = 'Default text'
        Label(self.top, text=labeltext).pack()

    def add_button(self, button):
        self.buttons.append(button)
        button.pack(pady=5)

    def cancel(self):
        self.top.destroy()

# Класс приложения
class App(Tk):
    def __init__(self, buttons, plotter, commands, entries):
        super().__init__()
        self.buttons = buttons
        self.plotter = plotter
        self.commands = commands
        self.entries = entries
        self.entries.set_parent_window(self)
        self.plotter.set_parent_window(self)
        self.commands.set_parent_window(self)
        self.buttons.set_parent_window(self)

    def add_button(self, name, text, command_name, *args, **kwargs):
        hot_key = kwargs.get('hot_key')
        if hot_key:
            kwargs.pop('hot_key')
        callback = partial(self.commands.get_command_by_name(command_name), *args, **kwargs)
        new_button = self.buttons.add_button(name=name, text=text, command=callback)
        if hot_key:
            self.bind(hot_key, callback)
        new_button.pack(fill=BOTH)

    def get_button_by_name(self, name):
        return self.buttons.buttons.get(name)

    def create_menu(self):
        menu = Menu(self)
        self.config(menu=menu)

        file_menu = Menu(menu)
        file_menu.add_command(label="Save as...", command=self.commands.get_command_by_name('save_as'))
        file_menu.add_command(label="Load session...", command=self.commands.get_command_by_name('load_session'))  # Добавляем команду загрузки сессии
        menu.add_cascade(label="File", menu=file_menu)

if __name__ == "__main__":
    # Инициализация кнопок
    buttons_main = Buttons()
    # Инициализация отрисовщика графиков
    plotter_main = Plotter()
    # Инициализация команд для выполнения при нажатии кнопок или горячих клавиш
    commands_main = Commands()
    # Инициализация текстовых полей
    entries_main = Entries()
    # Регистрация команд
    commands_main.add_command('plot', commands_main.plot)
    commands_main.add_command('add_func', commands_main.add_func)
    commands_main.add_command('save_as', commands_main.save_as)
    commands_main.add_command('load_session', commands_main.load_session)  # Регистрация команды загрузки сессии
    commands_main.add_command('delete_active_entry', entries_main.delete_active_entry)
    commands_main.add_command('delete_last_entry', entries_main.delete_last_entry)
    # Инициализация приложения
    app = App(buttons_main, plotter_main, commands_main, entries_main)
    # Добавление кнопки добавления новой функции
    app.add_button('add_func', 'Добавить функцию', 'add_func', hot_key='<Control-a>')
    # Добавление кнопки удаления активного текстового поля
    app.add_button('delete_entry', 'Удалить текстовое поле', 'delete_active_entry', hot_key='<Control-d>')
    # Добавление кнопки удаления последнего текстового поля
    app.add_button('delete_last_entry', 'Удалить последнее текстовое поле', 'delete_last_entry', hot_key='<Control-n>')
    # Добавление первого текстового поля
    entries_main.add_entry()
    app.create_menu()

    # Добавление обработчика для комбинации клавиш Ctrl + D
    app.bind('<Control-d>', lambda event: app.commands.get_command_by_name('delete_active_entry')())

    # Добавление обработчика для комбинации клавиш Ctrl + N
    app.bind('<Control-n>', lambda event: app.commands.get_command_by_name('delete_last_entry')())

    # Запуск приложения
    app.mainloop()
