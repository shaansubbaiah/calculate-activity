# -*- coding: utf-8 -*-
# layout.py, sugar calculator, by:
#   Reinier Heeres <reinier@heeres.eu>
#   Miguel Alvarez <miguel@laptop.org>
#   Aneesh Dogra <lionaneesh@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os

from gettext import gettext as _
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
import sugar3.profile
from sugar3.graphics.combobox import ComboBox
from toolbars import EditToolbar
from toolbars import AlgebraToolbar
from toolbars import TrigonometryToolbar
from toolbars import BooleanToolbar
from toolbars import MiscToolbar
from toolbars import ColorToolbar

import numParser

try:
    from sugar3.graphics.toolbarbox import ToolbarButton, ToolbarBox
    from sugar3.graphics.toolbutton import ToolButton
    from sugar3.activity.widgets import ActivityToolbarButton
    from sugar3.activity.widgets import StopButton
except ImportError:
    pass


def create_color(rf, gf, bf, alpha=1):
    return Gdk.RGBA(rf, gf, bf, alpha)


color_digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

default_color_constants = {
    1: create_color(0.0, 0.0, 0.0),
    2: create_color(0.3, 0.0, 0.1),
    3: create_color(1.0, 0.0, 0.0),
    4: create_color(1.0, 0.5, 0.0),
    5: create_color(1.0, 1.0, 0.0),
    6: create_color(0.0, 1.0, 0.0),
    7: create_color(0.0, 0.0, 1.0),
    8: create_color(1.0, 0.0, 1.0),
    9: create_color(0.8, 0.8, 0.8),
    0: create_color(1.0, 1.0, 1.0)
}

class CalcLayout:

    FONT_SMALL_POINTS = 10
    FONT_SMALL = "sans %d" % FONT_SMALL_POINTS
    FONT_SMALL_NARROW = "sans italic %d" % FONT_SMALL_POINTS
    FONT_BIG_POINTS = 14
    FONT_BIG = "sans bold %d" % FONT_BIG_POINTS
    FONT_BIG_NARROW = "sans italic 14"
    FONT_BIGGER_POINTS = 18
    FONT_BIGGER = "sans bold %d" % FONT_BIGGER_POINTS

    def __init__(self, parent):
        self._parent = parent

        self._own_equations = []
        self._other_equations = []
        self._showing_history = True
        self._showing_all_history = True
        self._var_textviews = {}
        self.graph_selected = None
        self.digit_color = {}
        self.preset_default_color()
        self.create_dialog()

    def set_digit_color(self, bgcol):
        r, g, b = bgcol.to_color().to_floats()
        bright = (r + g + b) / 3.0
        if bright < 0.5:
            return self.col_white
        else:
            return self.col_black

    def preset_default_color(self):
        try:
            f = open(self._parent.bg_path, 'r')
            if os.path.getsize(self._parent.bg_path) == 0:
                for num in range(0, 10):
                    self.digit_color[num] = create_color(0.50, 0.50, 0.50)
                return
            check_num = 0
            for each_line in f:
                each_line = each_line.rstrip('\n')
                colors = each_line.split(' ')
                num = colors[0]
                if int(num) == check_num:
                    check_num += 1
                else:
                    raise Exception()
                self.digit_color[int(num)] = create_color(float(colors[1]),
                                             float(colors[2]), float(colors[3]))
        except Exception, IOError:
            for num in range(0, 10):
                self.digit_color[num] = create_color(0.50, 0.50, 0.50)

    def create_button_data(self):
        """Create a list with button information. We need to do that here
        because we want to include the lambda functions."""

        mul_sym = self._parent.ml.mul_sym
        div_sym = self._parent.ml.div_sym
        equ_sym = self._parent.ml.equ_sym

        self.button_data = [
            # [x, y, width, label, bgcol, cb]
            [0, 0, 2, 1, u'\u2190', self.col_gray3,
                lambda w: self._parent.move_left()],
            [2, 0, 2, 1, u'\u2192', self.col_gray3,
                lambda w: self._parent.move_right()],
            [4, 0, 2, 1, u'\u232B', self.col_gray3,
                lambda w: self._parent.remove_character(-1)],

            [0, 1, 1, 2, numParser.local('7'), self.digit_color[7],
                lambda w: self._parent.add_text(numParser.local('7'))],
            [1, 1, 1, 2, numParser.local('8'), self.digit_color[8],
                lambda w: self._parent.add_text(numParser.local('8'))],
            [2, 1, 1, 2, numParser.local('9'), self.digit_color[9],
                lambda w: self._parent.add_text(numParser.local('9'))],

            [0, 3, 1, 2, numParser.local('4'), self.digit_color[4],
                lambda w: self._parent.add_text(numParser.local('4'))],
            [1, 3, 1, 2, numParser.local('5'), self.digit_color[5],
                lambda w: self._parent.add_text(numParser.local('5'))],
            [2, 3, 1, 2, numParser.local('6'), self.digit_color[6],
                lambda w: self._parent.add_text(numParser.local('6'))],

            [0, 5, 1, 2, numParser.local('1'), self.digit_color[1],
                lambda w: self._parent.add_text(numParser.local('1'))],
            [1, 5, 1, 2, numParser.local('2'), self.digit_color[2],
                lambda w: self._parent.add_text(numParser.local('2'))],
            [2, 5, 1, 2, numParser.local('3'), self.digit_color[3],
                lambda w: self._parent.add_text(numParser.local('3'))],

            [0, 7, 2, 2, numParser.local('0'), self.digit_color[0],
                lambda w: self._parent.add_text(numParser.local('0'))],

            [2, 7, 1, 2, '.', self.col_gray2,
                lambda w: self._parent.add_text('.')],

            [3, 1, 3, 2, _('Clear'), self.col_gray1,
             lambda w: self._parent.clear()],

            [3, 3, 1, 2, '+', self.col_gray3,
                lambda w: self._parent.add_text('+')],
            [4, 3, 1, 2, '-', self.col_gray3,
                lambda w: self._parent.add_text('-')],
            [5, 3, 1, 2, '(', self.col_gray3,
             lambda w: self._parent.add_text('(')],
            [3, 5, 1, 2, mul_sym, self.col_gray3,
                lambda w: self._parent.add_text(mul_sym)],
            [4, 5, 1, 2, div_sym, self.col_gray3,
                lambda w: self._parent.add_text(div_sym)],
            [5, 5, 1, 2, ')', self.col_gray3,
                lambda w: self._parent.add_text(')')],

            [3, 7, 3, 2, equ_sym, self.col_gray1,
                lambda w: self._parent.process()]
        ]

    def create_dialog(self):
        """Setup most of the dialog."""

# Toolbar
        self._toolbar_box = ToolbarBox()
        activity_button = ActivityToolbarButton(self._parent)
        self._toolbar_box.toolbar.insert(activity_button, 0)

        def append(icon_name, label, page, position):
            toolbar_button = ToolbarButton()
            toolbar_button.props.page = page
            toolbar_button.props.icon_name = icon_name
            toolbar_button.props.label = label
            self._toolbar_box.toolbar.insert(toolbar_button, position)
        append('toolbar-edit',
               _('Edit'),
               EditToolbar(self._parent),
               -1)
        append('toolbar-algebra',
               _('Algebra'),
               AlgebraToolbar(self._parent),
               -1)
        append('toolbar-trigonometry',
               _('Trigonometry'),
               TrigonometryToolbar(self._parent),
               -1)
        append('toolbar-boolean',
               _('Boolean'),
               BooleanToolbar(self._parent),
               -1)
        self._misc_toolbar = MiscToolbar(
            self._parent,
            target_toolbar=self._toolbar_box.toolbar)
        append('toolbar-constants',
               _('Miscellaneous'),
               self._misc_toolbar,
               5)

        self._preset_button = ToolButton(icon_name='preset',
                              tooltip=_('Set color layout'))
        self._preset_button.connect('clicked', self._use_preset_color)
        self._toolbar_box.toolbar.insert(self._preset_button, -1)

        self._reset_button = ToolButton(icon_name='reset',
                             tooltip=_('Revert back to default color layout'))
        self._reset_button.connect('clicked', self._reset_layout)
        self._toolbar_box.toolbar.insert(self._reset_button, -1)

        append('toolbar-color',
               _('Change Layout Color'),
               ColorToolbar(self),
               -1)
        self._stop_separator = Gtk.SeparatorToolItem()
        self._stop_separator.props.draw = False
        self._stop_separator.set_expand(True)
        self._stop_separator.show()
        self._toolbar_box.toolbar.insert(self._stop_separator, -1)

        self._stop = StopButton(self._parent)
        self._toolbar_box.toolbar.insert(self._stop, -1)
        self._toolbar_box.show_all()
        self._parent.set_toolbar_box(self._toolbar_box)

# Some layout constants
        self.input_font = Pango.FontDescription('sans bold 12')
        self.button_font = Pango.FontDescription('sans bold 16')
        self.col_white = create_color(1.00, 1.00, 1.00)
        self.col_gray1 = create_color(0.76, 0.76, 0.76)
        self.col_gray2 = create_color(0.50, 0.50, 0.50)
        self.col_gray3 = create_color(0.25, 0.25, 0.25)
        self.col_black = create_color(0.00, 0.00, 0.00)
        self.col_red = create_color(1.00, 0.00, 0.00)

# Big - Table, 16 rows, 10 columns, homogeneously divided
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_spacing(0)
        self.grid.set_column_spacing(4)

# Left part: container and input
        vc1 = Gtk.VBox(False, 0)
        hc1 = Gtk.HBox(False, 10)
        eb = Gtk.EventBox()
        eb.add(hc1)
        eb.override_background_color(Gtk.StateType.NORMAL, self.col_black)
        eb.set_border_width(12)
        eb2 = Gtk.EventBox()
        eb2.add(eb)
        eb2.override_background_color(Gtk.StateType.NORMAL, self.col_black)
        label1 = Gtk.Label(label=_('Label:'))
        label1.override_color(Gtk.StateType.NORMAL, self.col_white)
        label1.set_alignment(1, 0.5)
        hc1.pack_start(label1, expand=False, fill=False, padding=10)
        self.label_entry = Gtk.Entry()
        self.label_entry.override_background_color(Gtk.StateFlags.INSENSITIVE, self.col_black)
        hc1.pack_start(self.label_entry, expand=True, fill=True, padding=0)
        vc1.pack_start(eb2, False, True, 0)

        self.text_entry = Gtk.Entry()
        try:
            self.text_entry.props.im_module = 'gtk-im-context-simple'
        except AttributeError:
            pass
        self.text_entry.set_size_request(-1, 75)
        self.text_entry.connect('key_press_event', self._parent.ignore_key_cb)
        self.text_entry.modify_font(self.input_font)
        self.text_entry.override_background_color(Gtk.StateFlags.INSENSITIVE, self.col_black)
        eb = Gtk.EventBox()
        eb.add(self.text_entry)
        eb.override_background_color(Gtk.StateFlags.NORMAL, self.col_black)
        eb.set_border_width(12)
        eb2 = Gtk.EventBox()
        eb2.add(eb)
        eb2.override_background_color(Gtk.StateType.NORMAL, self.col_black)
        vc1.pack_start(eb2, expand=True, fill=True, padding=0)
        self.grid.attach(vc1, 0, 0, 7, 6)

# Left part: buttons
        self.pad = Gtk.Grid()
        self.pad.set_column_homogeneous(True)
        self.pad.set_row_spacing(6)
        self.pad.set_column_spacing(6)
        self.create_button_data()
        self.buttons = {}
        for x, y, w, h, cap, bgcol, cb in self.button_data:
            fgcol = self.set_digit_color(bgcol)
            button = self.create_button(
                _(cap), cb, fgcol, bgcol, w, h)
            self.buttons[cap] = button
            self.pad.attach(button, x, y, w, h)

        eb = Gtk.EventBox()
        eb.add(self.pad)
        eb.override_background_color(Gtk.StateType.NORMAL, self.col_black)
        self.grid.attach(eb, 0, 6, 7, 20)

# Right part: container and equation button
        hc2 = Gtk.HBox()
        combo = ComboBox()
        combo.append_item(0, _('All equations'))
        combo.append_item(1, _('My equations'))
        combo.append_item(2, _('Show variables'))
        combo.set_active(0)
        combo.connect('changed', self._history_filter_cb)
        hc2.pack_start(combo, True, True, 0)
        hc2.set_border_width(6)
        self.grid.attach(hc2, 7, 0, 4, 2)

# Right part: last equation
        self.last_eq = Gtk.TextView()
        self.last_eq.set_editable(False)
        self.last_eq.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.last_eq.connect('realize', self._textview_realize_cb)
        self.last_eq.modify_base(Gtk.StateType.NORMAL, Gdk.color_parse(
                                 sugar3.profile.get_color().get_fill_color()))
        self.last_eq.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(
                               sugar3.profile.get_color().get_stroke_color()))
        self.last_eq.set_border_window_size(Gtk.TextWindowType.LEFT, 4)
        self.last_eq.set_border_window_size(Gtk.TextWindowType.RIGHT, 4)
        self.last_eq.set_border_window_size(Gtk.TextWindowType.TOP, 4)
        self.last_eq.set_border_window_size(Gtk.TextWindowType.BOTTOM, 4)

        # TODO Fix for old Sugar 0.82 builds, red_float not available
        xo_color = sugar3.profile.get_color()
        bright = (
            Gdk.color_parse(xo_color.get_fill_color()).red_float + \
            Gdk.color_parse(xo_color.get_fill_color()).green_float + \
            Gdk.color_parse(xo_color.get_fill_color()).blue_float) / 3.0
        if bright < 0.5:
            self.last_eq.modify_text(Gtk.StateType.NORMAL,
                                     self.col_white.to_color())
        else:
            self.last_eq.modify_text(Gtk.StateType.NORMAL,
                                     self.col_black.to_color())

        self.grid.attach(self.last_eq, 7, 2, 4, 5)

# Right part: history
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER,
                                   Gtk.PolicyType.AUTOMATIC)

        self.history_vbox = Gtk.VBox()
        self.history_vbox.set_homogeneous(False)
        self.history_vbox.set_border_width(0)
        self.history_vbox.set_spacing(4)

        self.variable_vbox = Gtk.VBox()
        self.variable_vbox.set_homogeneous(False)
        self.variable_vbox.set_border_width(0)
        self.variable_vbox.set_spacing(4)

        vbox = Gtk.VBox()
        vbox.pack_start(self.history_vbox, True, True, 0)
        vbox.pack_start(self.variable_vbox, True, True, 0)
        scrolled_window.add_with_viewport(vbox)
        self.grid.attach(scrolled_window, 7, 7, 4, 19)

        Gdk.Screen.get_default().connect('size-changed',
                                         self._configure_cb)

    def _ColorToolbar__change_layout_color_cb(self, widget, num):
        cdia = Gtk.ColorSelectionDialog("Select Layout Color", self._parent)
        colorsel = cdia.get_color_selection()
        colorsel.set_current_rgba(self.digit_color[int(num)])
        cdia.set_transient_for(self._parent)
        cdia.set_modal(1)
        response = cdia.run()
        if response == -5:
            color = cdia.get_color_selection().props.current_color.to_floats()
            self.digit_color[int(num)] = create_color(color[0],
                                                      color[1], color[2])
            for btn in self.button_data:
                if(btn[4] == num):
                    btn_width = btn[2]
                    btn_height = btn[3]
                    btn_label = btn[4]
                    btn_bgcol = self.digit_color[int(num)]
                    btn_fgcol = self.set_digit_color(btn_bgcol)
                    self.modify_button_appearance(self.buttons[btn_label],
                                                  btn_fgcol, btn_bgcol, btn_width, btn_height)
            cdia.destroy()
        elif response == -6:
            cdia.destroy()

    def change_layout_color(self):
        for button in self.button_data:
            label = button[4]
            if label in color_digits:
                bg_color = self.digit_color[int(label)]
                width = button[2]
                height = button[3]
                fg_color = self.set_digit_color(bg_color)
                self.modify_button_appearance(self.buttons[label],
                                             fg_color, bg_color, width, height)

    def _reset_layout(self, reset_btn):
        for num in range(0, 10):
            self.digit_color[num] = self.col_gray2
        self.change_layout_color()

    def _use_preset_color(self, preset_btn):
        for num in range(0, 10):
            self.digit_color[num] = default_color_constants[num]
        self.change_layout_color()

    def _configure_cb(self, event):
        # Maybe redo layout
        self._toolbar_box.toolbar.remove(self._stop)
        self._toolbar_box.toolbar.remove(self._stop_separator)
        self._misc_toolbar.update_layout()
        self._toolbar_box.toolbar.insert(self._stop_separator, -1)
        self._toolbar_box.toolbar.insert(self._stop, -1)

    def show_it(self):
        """Show the dialog."""
        self._parent.set_canvas(self.grid)
        self._parent.show_all()
        self.show_history()
        self.text_entry.grab_focus()

    def showing_history(self):
        """Return whether we're currently showing the history (or otherwise
        the list of variables)."""
        return self._showing_history

    def show_history(self):
        """Show the history VBox."""
        self._showing_history = True
        self.variable_vbox.hide()
        self.history_vbox.show()

    def toggle_select_graph(self, widget, host=None):
        # if we have a graph already selected, we must deselect it first
        if self.graph_selected and self.graph_selected != widget:
            self.toggle_select_graph(self.graph_selected)

        if not self.graph_selected:
            widget.set_visible_window(True)
            widget.set_above_child(True)
            self.graph_selected = widget
            white = create_color(1.0, 1.0, 1.0)
            widget.override_background_color(Gtk.StateType.NORMAL, white)
        else:
            widget.set_visible_window(False)
            self.graph_selected = False

    def add_equation(self, textview, own, prepend=False):
        """Add a Gtk.TextView of an equation to the history_vbox."""

        GraphEventBox = None
        if isinstance(textview, Gtk.Image):
            # Add the image inside the eventBox
            GraphEventBox = Gtk.EventBox()
            GraphEventBox.add(textview)
            GraphEventBox.set_visible_window(False)
            GraphEventBox.connect(
                'button_press_event', self.toggle_select_graph)
            GraphEventBox.show()

        if prepend:
            if GraphEventBox:
                self.history_vbox.pack_start(GraphEventBox, False, True, 0)
                self.history_vbox.reorder_child(GraphEventBox, 0)
            else:
                self.history_vbox.pack_start(textview, False, True, 0)
                self.history_vbox.reorder_child(textview, 0)
        else:
            if GraphEventBox:
                self.history_vbox.pack_end(GraphEventBox, False, True)
            else:
                self.history_vbox.pack_end(textview, False, True)

        if own:
            if GraphEventBox:
                self._own_equations.append(GraphEventBox)
                GraphEventBox.get_child().show()
            else:
                self._own_equations.append(textview)
                textview.show()
        else:
            if self._showing_all_history:
                if GraphEventBox:
                    self._other_equations.append(GraphEventBox)
                    GraphEventBox.get_child().show()
                else:
                    self._other_equations.append(textview)
                    textview.show()

    def show_all_history(self):
        """Show both owned and other equations."""
        self._showing_all_history = True
        for key in self._other_equations:
            if isinstance(key, Gtk.EventBox):
                key.get_child().show()
            else:
                key.show()

    def show_own_history(self):
        """Show only owned equations."""
        self._showing_all_history = False
        for key in self._other_equations:
            if isinstance(key, Gtk.EventBox):
                key.get_child().hide()
            else:
                key.hide()

    def add_variable(self, varname, textview):
        """Add a Gtk.TextView of a variable to the variable_vbox."""

        if varname in self._var_textviews:
            self.variable_vbox.remove(self._var_textviews[varname])
            del self._var_textviews[varname]

        self._var_textviews[varname] = textview
        self.variable_vbox.pack_start(textview, False, True, 0)

        # Reorder textviews for a sorted list
        names = self._var_textviews.keys()
        names.sort()
        for i in range(len(names)):
            self.variable_vbox.reorder_child(self._var_textviews[names[i]], i)

        textview.show()

    def show_variables(self):
        """Show the variables VBox."""
        self._showing_history = False
        self.history_vbox.hide()
        self.variable_vbox.show()

    def create_button(self, cap, cb, fgcol, bgcol, width, height):
        """Create a button that is set up properly."""
        button = Gtk.Button(_(cap))
        self.modify_button_appearance(button, fgcol, bgcol, width, height)
        button.connect("clicked", cb)
        button.connect("key_press_event", self._parent.ignore_key_cb)
        return button

    def modify_button_appearance(self, button, fgcol, bgcol, width, height):
        """Modify button style."""
        width = 50 * width
        height = 50 * height
        button.get_child().set_size_request(width, height)
        button.get_child().modify_font(self.button_font)
        button.get_child().override_color(Gtk.StateType.NORMAL, fgcol)
        button.override_background_color(Gtk.StateFlags.NORMAL, bgcol)
        button.override_background_color(Gtk.StateFlags.PRELIGHT, bgcol)

    def _history_filter_cb(self, combo):
        selection = combo.get_active()
        if selection == 0:
            self.show_history()
            self.show_all_history()
        elif selection == 1:
            self.show_history()
            self.show_own_history()
        elif selection == 2:
            self.show_variables()

    def _textview_realize_cb(self, widget):
        '''Change textview properties once window is created.'''
        win = widget.get_window(Gtk.TextWindowType.TEXT)
        win.set_cursor(Gdk.Cursor.new(Gdk.CursorType.HAND1))
        return False