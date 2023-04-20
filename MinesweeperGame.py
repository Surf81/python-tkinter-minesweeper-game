import tkinter as tk
from itertools import chain
from random import shuffle
from tkinter.messagebox import showinfo, showerror


# FLAG_SUMB = "⚑"
FLAG_SUMB = "\U0001F480"
MINE_SUMB = "\U0001F4A3"


class MineSweeperGameMenu(tk.Menu):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.__create_menu()

    def __create_menu(self):
        self.settings = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Жми сюда", menu=self.settings)

    def add_menu_item(self, label, command):
        self.settings.add_command(label=label, command=command)

    def add_game_settings(self, label, preferences, setpref):
        self.settings.add_command(label=label, command=self.__run_preferences_window(preferences, setpref))

    def __run_preferences_window(self, getpref, callback):
        def command(wintoclose, *args, **kwargs):
            wintoclose.destroy()
            callback(*args, **kwargs)

        def run():
            context = getpref()
            self.__open_preferences_window(context, command)

        return run

    def accept_result(self, wintoclose, row_e, col_e, mines_e, command):
        try:
            rows = int(row_e.get().strip())
            cols = int(col_e.get().strip())
            mines = int(mines_e.get().strip())
        except:
            showinfo("Неверное значениее значение", "Допускается вводить только целочисленные значения")
        else:
            if rows * cols * mines == 0:
                showinfo("Неверное значение", "Нулевые значения не допускаются")
            elif rows < 5 or cols < 5:
                showinfo("Неверное значение", "Минимальное количество рядов и колонок: 5")
            elif mines < 1:
                showinfo("Неверное значение", "Минимальное количество мин: 1")
            elif mines > cols * rows // 2:
                showinfo("Неверное значение", "Количество мин превышает 50% полей")
            else:
                command(wintoclose, rows, cols, mines)

    @staticmethod
    def __set_center_window(win):
        win.update_idletasks()
        width = win.winfo_width()
        frm_width = win.winfo_rootx() - win.winfo_x()
        win_width = width + 2 * frm_width
        height = win.winfo_height()
        titlebar_height = win.winfo_rooty() - win.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = win.winfo_screenwidth() // 2 - win_width // 2
        y = win.winfo_screenheight() // 2 - win_height // 2
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        win.deiconify()

    def __open_preferences_window(self, context: dict, command):
        if type(context) != dict:
            context = dict()

        settings_window = tk.Toplevel(self.master)
        settings_window.wm_title("Настройки игры")
        row_entry = tk.Entry(settings_window)
        row_entry.grid(row=0, column=1, pady=20, padx=20)
        tk.Label(settings_window, text="Количество рядов").grid(row=0, column=0, padx=20, sticky="w")
        row_entry.insert(0, context.get("rows", 5))

        col_entry = tk.Entry(settings_window)
        col_entry.grid(row=1, column=1, pady=20, padx=20)
        tk.Label(settings_window, text="Количество колонок").grid(row=1, column=0, padx=20, sticky="w")
        col_entry.insert(0, context.get("cols", 5))

        mines_entry = tk.Entry(settings_window)
        mines_entry.grid(row=2, column=1, pady=20, padx=20)
        tk.Label(settings_window, text="Количество мин").grid(row=2, column=0, padx=20, sticky="w")
        mines_entry.insert(0, context.get("mines", 5))

        tk.Button(settings_window, text="Применить",
                  command=lambda: self.accept_result(settings_window,
                                                     row_entry, col_entry, mines_entry,
                                                     command)
                  ).grid(row=3, column=0, padx=20, pady=20, sticky="we")

        self.__set_center_window(settings_window)

class MineField(tk.Button):
    def __init__(self, master, row, col, count, *args, **kwargs):
        super().__init__(master, width=3,
                         font="Arial 15 bold",
                         borderwidth=1,
                         *args, **kwargs)
        self.row = row
        self.col = col
        self.fieldcount = count
        self.mine = False
        self.opened = False
        self.checked = False

    def __repr__(self):
        return "Field {}:{}-{}={}".format(self.row, self.col, self.fieldcount, self.mine)


class StatusFrame(tk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        pass

        tk.Label(self, text="Мины на поле:").grid(row=0, column=0, padx=5)
        tk.Label(self, text="Найдено:").grid(row=0, column=2, padx=5)

        self.mine_lab_all = tk.Label(self, text="")
        self.mine_lab_all.grid(row=0, column=1)
        self.mine_lab_find = tk.Label(self, text="")
        self.mine_lab_find.grid(row=0, column=3)

    def show_all_mines(self, mines):
        self.mine_lab_all["text"] = str(mines)

    def show_checked_mines(self, mines):
        self.mine_lab_find["text"] = str(mines)


class MineSweeperGame(object):
    storage = {}
    mainwindow = tk.Tk()

    GAME_OVER = False
    ROWS = 10
    COLS = 7
    MINES = 10
    FIELD_COLORS = {
        1: "#25D500",
        2: "#1240AB",
        3: "#FF9500",
        4: "#C30083",
        5: "#560eAD",
        6: "#FFE800",
        7: "#009E8E",
        8: "#E40045",
    }

    def __init__(self):
        self.__dict__ = self.storage
        self.mainwindow.title("Саперушка")

    def start_app(self):
        self.__init_menu()
        self.__init_frames()
        self.__init_new_game()
        self.__set_center_window(self.mainwindow)
        self.mainwindow.mainloop()

#########################################
#                                       #
#   Блок инициализации главного меню    #
#                                       #
#########################################

    @classmethod
    def __set_preferences_cls(cls, rows, cols, mines):
        cls.ROWS = rows
        cls.COLS = cols
        cls.MINES = mines

    def __set_preferences(self, rows, cols, mines):
        self.__set_preferences_cls(rows, cols, mines)
        self.__del_fields()
        self.__init_new_game()

    def __get_preferences(self):
        return {
            "rows": self.ROWS,
            "cols": self.COLS,
            "mines": self.MINES
        }

    def __init_menu(self):
        self.mainmenu = MineSweeperGameMenu(self.mainwindow)
        self.mainwindow.config(menu=self.mainmenu)

        self.mainmenu.add_menu_item("Рискну здоровьем!", self.__start_new_game)
        self.mainmenu.add_game_settings("Поставлю свечку...",
                                        preferences=self.__get_preferences,
                                        setpref=self.__set_preferences)
        self.mainmenu.add_menu_item("Все! Я увольняюсь!", self.mainwindow.destroy)


#########################################
#                                       #
#   Блок инициализации игрового поля    #
#                                       #
#########################################

    @staticmethod
    def __set_center_window(win):
        win.update_idletasks()
        width = win.winfo_width()
        frm_width = win.winfo_rootx() - win.winfo_x()
        win_width = width + 2 * frm_width
        height = win.winfo_height()
        titlebar_height = win.winfo_rooty() - win.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = win.winfo_screenwidth() // 2 - win_width // 2
        y = win.winfo_screenheight() // 2 - win_height // 2
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        win.deiconify()

    def __init_frames(self):
        self.mainframe = tk.Frame(self.mainwindow, bd=4, relief=tk.GROOVE)
        self.mainframe.grid(row=0, column=0, sticky="wens")

        self.statusframe = StatusFrame(self.mainwindow, bd=4, relief=tk.FLAT)
        self.statusframe.grid(row=1, column=0, sticky="wens")

        tk.Grid.columnconfigure(self.mainwindow, 0, weight=1)
        tk.Grid.rowconfigure(self.mainwindow, 0, weight=self.ROWS)

    def __init_new_game(self):
        self.mainwindow.attributes('-alpha', 0.0)
        self.__del_fields()
        self.__init_fields(self.mainframe)
        self.__create_fields()
        self.__put_mines()
        self.statusframe.show_all_mines(self.MINES)
        self.statusframe.show_checked_mines(self.checked_fields)
        # self.__pprint_fields()
        self.mainwindow.attributes('-alpha', 1.0)
        self.GAME_STARTED = False

    def __del_fields(self):
        for el in self.mainframe.winfo_children():
            if type(el) == MineField:
                el.destroy()

    def __init_fields(self, win):
        self.allfields = []
        self.checked_fields = 0
        for row in range(self.ROWS):
            fieldsline = []
            for col in range(self.COLS):
                count = row * self.COLS + col
                fld = MineField(win,
                                row=row,
                                col=col,
                                count=count,
                                state=tk.DISABLED,
                                bg="grey")
                fld.config(command=lambda field=fld: self.__demining(field))
                fld.bind("<Button-3>", self.__check_mine)
                fld.bind("<Double-Button-1>", self.__speed_demining)
                fieldsline.append(fld)
            self.allfields.append(fieldsline)

    def __create_fields(self):
        for row in range(self.ROWS):
            for col in range(self.COLS):
                self.allfields[row][col].grid(row=row, column=col, sticky="wens")
                tk.Grid.columnconfigure(self.mainframe, col, weight=1)
            tk.Grid.rowconfigure(self.mainframe, row, weight=1)

    def __put_mines(self):
        fields = list(range(self.COLS * self.ROWS))
        shuffle(fields)
        mine_places = fields[:self.MINES]
        for fld in chain(*self.allfields):
            if fld.fieldcount in mine_places:
                fld.mine = True

    def __start_new_game(self):
        if self.GAME_STARTED:
            self.__init_new_game()

        for fld in chain(*self.allfields):
            fld.config(stat=tk.NORMAL, bg="lightgrey")
        self.GAME_STARTED = True
        self.GAME_FINISHED = False

    def __game_over(self, mine_explode=None):
        self.GAME_FINISHED = True
        for row in range(self.ROWS):
            for col in range(self.COLS):
                fld = self.allfields[row][col]
                fld.config(state=tk.DISABLED)
                if fld != mine_explode:
                    fld.config(bg="grey")
                if fld.mine:
                    fld.config(text=MINE_SUMB, disabledforeground="black")
                    if fld.checked:
                        fld.config(bg="lightgreen")

    def __game_fail(self, target):
        self.__game_over(target)
        showerror("БУУУУМ!!!!", "Не отчаивайся! Сапер ошибается лишь однажды!")

    def __game_win(self):
        self.__game_over()
        showinfo("Да как так-то ???", "Не радуйся! Тебе просто повезло!")

    def __is_win(self):
        if sum((fld.mine and fld.checked) or fld.opened for fld in chain(*self.allfields)) == self.ROWS * self.COLS:
            return True
        return False


#########################################
#                                       #
#   Действия пользователя               #
#                                       #
#########################################

    def __open_field(self, field: MineField):
        fields_around = []
        count = 0
        for row in range(max(field.row - 1, 0), min(field.row + 2, self.ROWS)):
            for col in range(max(field.col - 1, 0), min(field.col + 2, self.COLS)):
                fld = self.allfields[row][col]
                if fld.mine:
                    count += 1
                elif not (fld.opened or fld.checked):
                    fields_around.append(fld)
        if count:
            field.config(text=count, disabledforeground=self.FIELD_COLORS[count])
        else:
            for fld in fields_around:
                self.__demining(fld)

    def __demining(self, clicked_field: MineField):
        if not self.GAME_STARTED or self.GAME_FINISHED:
            return

        clicked_field.opened = True
        clicked_field.config(state=tk.DISABLED, relief=tk.SUNKEN, bg="white")
        if clicked_field.mine:
            clicked_field.config(text=MINE_SUMB, bg="red", disabledforeground="black")
            self.__game_fail(clicked_field)
            return
        else:
            self.__open_field(clicked_field)

        if self.checked_fields == self.MINES:
            if self.__is_win():
                self.__game_win()

    def __speed_demining(self, event):
        if not self.GAME_STARTED or self.GAME_FINISHED:
            return

        current_field = event.widget
        if current_field.opened:
            fields_around = []
            for row in range(max(current_field.row - 1, 0), min(current_field.row + 2, self.ROWS)):
                for col in range(max(current_field.col - 1, 0), min(current_field.col + 2, self.COLS)):
                    fld = self.allfields[row][col]
                    if not (fld.opened or fld.checked):
                        fields_around.append(fld)
            for fld in fields_around:
                self.__demining(fld)

    def __check_mine(self, event):
        if not self.GAME_STARTED or self.GAME_FINISHED:
            return

        current_field = event.widget
        if not current_field.opened:
            if current_field["state"] == tk.NORMAL:
                if self.checked_fields == self.MINES:
                    showinfo("Притормози!", "Мин всего {}!".format(self.MINES))
                else:
                    current_field["state"] = tk.DISABLED
                    current_field["text"] = FLAG_SUMB
                    current_field.checked = True
                    self.checked_fields += 1
                    self.statusframe.show_checked_mines(self.checked_fields)

                    if self.checked_fields == self.MINES:
                        if self.__is_win():
                            self.__game_win()


            elif current_field["text"] == FLAG_SUMB:
                current_field["state"] = tk.NORMAL
                current_field["text"] = ""
                current_field.checked = False
                self.checked_fields -= 1
                self.statusframe.show_checked_mines(self.checked_fields)

    def __pprint_fields(self):
        def get_field(field: MineField):
            if field.mine:
                return "B "
            count = 0
            for row in range(max(field.row - 1, 0), min(field.row + 2, self.ROWS)):
                for col in range(max(field.col - 1, 0), min(field.col + 2, self.COLS)):
                    fld = self.allfields[row][col]
                    if fld.mine:
                        count += 1
            return "{} ".format(count)

        print("\nПоследний раз подсказываю!")
        for line in self.allfields:
            print("".join(map(get_field, line)))


game = MineSweeperGame()
game.start_app()