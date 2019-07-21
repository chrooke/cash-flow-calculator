#!/usr/bin/env python
import os
import string
import re
import wx
import wx.adv
from datetime import date, timedelta
from cash_flow.transaction import Transaction
from cash_flow.transaction_store import TransactionStore
from cash_flow.cash_flow import CashFlow


def wxDate2pyDate(wxdate):
    return date(wxdate.GetYear(), wxdate.GetMonth()+1, wxdate.GetDay())

def pyDate2wxDate(pyDate):
    return wx.DateTime(pyDate.day, pyDate.month-1, pyDate.year)


class CashFlowDisplay(wx.Panel):
    def __init__(self, parent, ts):
        super().__init__(parent)
        self.ts = ts
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        # Controls at top
        self.control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, label='Starting Date')
        self.control_sizer.Add(label, 0)
        wxDate = pyDate2wxDate(date.today())
        self.date_picker = wx.adv.DatePickerCtrl(self)
        self.date_picker.SetValue(wxDate)
        self.date_picker.Bind(wx.adv.EVT_DATE_CHANGED, self.handleStartingInfoChange)   
        self.control_sizer.Add(self.date_picker, 0)
        label = wx.StaticText(self, label="Starting Balance $")
        self.control_sizer.Add(label, 0)
        self.starting_balance = wx.TextCtrl(self, value="0.00")
        self.starting_balance.Bind(wx.EVT_TEXT, self.handleStartingInfoChange)        
        self.control_sizer.Add(self.starting_balance, 0)
        self.main_sizer.Add(self.control_sizer, 0)
        # List of transactions
        self.list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.list_sizer, 0, wx.EXPAND)
        self.SetSizer(self.main_sizer)
        self.updateList()

    def handleStartingInfoChange(self, event):
        self.updateList()

    def updateList(self):
        start_date = wxDate2pyDate(self.date_picker.GetValue())
        starting_balance = self.starting_balance.GetValue()
        allow = string.digits + "."
        starting_balance = re.sub('[^%s]' % allow, '', starting_balance)
        cf = CashFlow(start_date, starting_balance, self.ts)
        day = cf.getTodaysTransactions()
        self.list_sizer.Clear(delete_windows=True)
        listCtrl = wx.ListCtrl(self, style=wx.LC_REPORT)
        listCtrl.InsertColumn(0, "Date")
        listCtrl.InsertColumn(1, "Balance")
        listCtrl.InsertColumn(2, "Transaction")
        listCtrl.InsertColumn(3, "Amount")
        listCtrl.SetColumnWidth(0, 100)
        listCtrl.SetColumnWidth(1, 100)
        listCtrl.SetColumnWidth(2, 200)
        listCtrl.SetColumnWidth(3, 75)
        for i in range(0, 365):
            (d, bal, t_list) = next(day)
            if t_list:
                # Add daily summary
                index = listCtrl.InsertItem(listCtrl.GetItemCount(), str(d))
                listCtrl.SetItem(index, 1, str(bal))
                if bal < 100:
                    listCtrl.SetItemBackgroundColour(index, wx.Colour(255, 255, 0))
                if bal < 0:
                    listCtrl.SetItemBackgroundColour(index, wx.Colour(255, 0, 0))
                # Add individual transactions
                for t in t_list:
                    index = listCtrl.InsertItem(listCtrl.GetItemCount(), "")
                    listCtrl.SetItem(index, 2, str(t.description))
                    listCtrl.SetItem(index, 3, str(t.amount))                 
                    # label = f'{d} {t.description} {t.amount} {bal}'
                    # txt = wx.StaticText(self, label=label)
                    # self.list_sizer.Add(txt,0)
        self.list_sizer.Add(listCtrl, 0, wx.EXPAND)
        self.main_sizer.Layout()


class TransactionManagement(wx.Panel):
    def __init__(self, parent, ts):
        super().__init__(parent)
        self.ts = ts
        self.editPane1 = None
        self.transaction_buttons = {}
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.left_side_sizer = wx.BoxSizer(wx.VERTICAL)
        self.t_list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.left_side_sizer.Add(self.t_list_sizer, 0)
        btn = wx.Button(self, label='New Transaction')
        btn.Bind(wx.EVT_BUTTON, self.newTransaction)
        self.left_side_sizer.Add(btn, 0)
        self.main_sizer.Add(self.left_side_sizer, 0)
        self.SetSizer(self.main_sizer)

    def redraw(self):
        self.clearEditPane()
        self.rebuildTransactionButtons()

    def clearEditPane(self):
        if self.main_sizer.GetItemCount() > 1:
            self.main_sizer.Remove(1)
            if self.editPane1:
                self.editPane1.Destroy()
                self.editPane1 = None
            self.main_sizer.Layout()

    def rebuildTransactionButtons(self):
        self.t_list_sizer.Clear(delete_windows=True)
        self.transaction_buttons = {}
        for t in self.ts.getTransactions():
            self.updateButtonForTransaction(t)
        self.main_sizer.Layout()

    def editTransaction(self, event, trans):
        self.clearEditPane()
        self.editPane1 = EditTransactionPanel(self, trans)
        self.main_sizer.Add(self.editPane1, 0)
        self.main_sizer.Layout()

    def newTransaction(self, event):
        t = Transaction()
        self.editTransaction(event, t)

    def deleteTransaction(self, trans):
        self.ts.removeTransactions(trans)
        self.rebuildTransactionButtons()

    def updateButtonForTransaction(self, t):
        label = f'{t.description} {t.amount} {t.start}'
        if t in self.transaction_buttons:
            btn = self.transaction_buttons[t]
            btn.SetLabel(label)
        else:
            btn = wx.Button(self, label=label)
            btn.Bind(wx.EVT_BUTTON, lambda evt, trans=t: self.editTransaction(evt, trans))
            self.t_list_sizer.Add(btn, 0)
            self.transaction_buttons[t] = btn
        if t not in self.ts.getTransactions():
            self.ts.addTransactions(t)
        self.t_list_sizer.Layout()


class EditTransactionPanel(wx.Panel):
    def __init__(self, parent, trans):
        super().__init__(parent)
        self.parent = parent
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.transaction = trans

        # Description

        self.description = wx.TextCtrl(self)
        self.main_sizer.Add(self.description, 0, wx.EXPAND)

        # Original Start Date
        label = wx.StaticText(self, label='Original Start Date', size=(50, -1))
        self.orig_start = wx.adv.DatePickerCtrl(self)
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer.Add(label, 0, wx.ALL, 5)
        row_sizer.Add(self.orig_start, 1, wx.ALL, 5)
        self.main_sizer.Add(row_sizer, 0)

        # Current Start Date
        label = wx.StaticText(self, label='Current Start Date', size=(50, -1))
        self.start = wx.adv.DatePickerCtrl(self)
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer.Add(label, 0, wx.ALL, 5)
        row_sizer.Add(self.start, 1, wx.ALL, 5)
        self.main_sizer.Add(row_sizer, 0)

        # Amount
        label = wx.StaticText(self, label='Amount', size=(50, -1))
        self.amount = wx.TextCtrl(self)
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer.Add(label, 0, wx.ALL, 5)
        row_sizer.Add(self.amount, 1, wx.ALL, 5)
        self.main_sizer.Add(row_sizer, 0)

        # Frequency
        label = wx.StaticText(self, label='Frequency', size=(50, -1))
        self.frequency = wx.Choice(self, choices=Transaction.INTERVALS)
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer.Add(label, 0, wx.ALL, 5)
        row_sizer.Add(self.frequency, 1, wx.ALL, 5)
        self.main_sizer.Add(row_sizer, 0)

        # Scheduled
        self.scheduled = wx.CheckBox(self, label='Scheduled', style=wx.CHK_2STATE | wx.ALIGN_RIGHT)
        self.main_sizer.Add(self.scheduled, 0)

        # Cleared
        self.cleared = wx.CheckBox(self, label='Cleared', style=wx.CHK_2STATE | wx.ALIGN_RIGHT)
        self.main_sizer.Add(self.cleared, 0)

        # Action Buttons
        action_button_sizer = wx.BoxSizer()

        cancel = wx.Button(self, label="Cancel")
        cancel.Bind(wx.EVT_BUTTON, self.cancelEdit)
        action_button_sizer.Add(cancel, 0)

        reset = wx.Button(self, label="Reset")
        reset.Bind(wx.EVT_BUTTON, self.resetEdit)
        action_button_sizer.Add(reset, 0)

        save = wx.Button(self, label="Save")
        save.Bind(wx.EVT_BUTTON, self.saveEdit)
        action_button_sizer.Add(save, 0)

        self.main_sizer.Add(action_button_sizer, 0)

        # Delete Button
        delete_button_sizer = wx.BoxSizer()
        delete = wx.Button(self, label="Delete")
        delete.Bind(wx.EVT_BUTTON, self.deleteTransaction)
        delete_button_sizer.Add(delete, 0)

        self.main_sizer.Add(delete_button_sizer, 0)

        self.setValues()

        self.SetSizer(self.main_sizer)

    def setValues(self):
        self.description.SetValue(self.transaction.description)
        self.orig_start.SetValue(pyDate2wxDate(self.transaction.original_start))
        self.start.SetValue(pyDate2wxDate(self.transaction.start))
        self.amount.SetValue(str(self.transaction.amount))
        self.frequency.SetSelection(Transaction.INTERVALS.index(self.transaction.frequency))
        self.scheduled.SetValue(self.transaction.scheduled)
        self.cleared.SetValue(self.transaction.cleared)

    def cancelEdit(self, event):
        self.parent.clearEditPane()

    def resetEdit(self, event):
        self.setValues()

    def saveEdit(self, event):
        self.transaction.description = self.description.GetValue()
        self.transaction.original_start = wxDate2pyDate(self.orig_start.GetValue())
        self.transaction.start = wxDate2pyDate(self.start.GetValue())
        self.transaction.amount = self.amount.GetValue()
        self.transaction.frequency = Transaction.INTERVALS[self.frequency.GetCurrentSelection()]
        self.transaction.scheduled = self.scheduled.GetValue()
        self.transaction.cleared = self.cleared.GetValue()
        self.parent.updateButtonForTransaction(self.transaction)
        self.parent.clearEditPane()

    def deleteTransaction(self, event):
        self.parent.deleteTransaction(self.transaction)
        self.parent.clearEditPane()


class MainFrame(wx.Frame):
    WILDCARD = "YAML (*.yml)|*.yml|"     \
               "All files (*.*)|*.*"

    def __init__(self):
        super().__init__(parent=None, title='Cash Flow Calculator')
        self.ts = TransactionStore()
        self.file = None
        self.notebook = wx.Notebook(self)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.handleNotebookChange)
        self.transactionManagement = TransactionManagement(self.notebook, self.ts)
        self.notebook.AddPage(self.transactionManagement, "Transaction Management")
        self.cashFlowDisplay = CashFlowDisplay(self.notebook, self.ts)
        self.notebook.AddPage(self.cashFlowDisplay, "Cash Flow")
        self.SetInitialSize(wx.Size(650, 650))
        self.create_menu()
        self.Show()

    def handleNotebookChange(self, event):
        self.updateChildren()
        event.Skip()

    def updateChildren(self):
        self.transactionManagement.redraw()
        self.cashFlowDisplay.updateList()

    def create_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        new_file_menu_item = file_menu.Append(
            wx.ID_ANY, "New File", "Create a new file"
        )
        open_file_menu_item = file_menu.Append(
            wx.ID_ANY, "Open...", "Open a file"
        )
        save_menu_item = file_menu.Append(
            wx.ID_ANY, "Save", "Save to current file"
        )
        save_as_menu_item = file_menu.Append(
            wx.ID_ANY, "Save As", "Save file with new name"
        )
        menu_bar.Append(file_menu, "&File")
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.on_new_file,
            source=new_file_menu_item,
        )
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.on_open_file,
            source=open_file_menu_item,
        )
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.on_save,
            source=save_menu_item,
        )
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.on_save_as,
            source=save_as_menu_item,
        )
        self.SetMenuBar(menu_bar)

    def on_new_file(self, event):
        self.loadTransactions()

    def on_open_file(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=MainFrame.WILDCARD,
            style=wx.FD_OPEN |
                  wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST |
                  wx.FD_PREVIEW
            )
        if dlg.ShowModal() == wx.ID_OK:
            self.loadTransactions(dlg.GetPath())
        dlg.Destroy()

    def on_save(self, event):
        if self.file is not None:
            self.saveTransactions()
        else:
            self.on_save_as(event)

    def on_save_as(self, event):
        if self.file is not None:
            defaultDir = os.path.dirname(self.file)
            defaultFile = os.path.basename(self.file)
        else:
            defaultDir = os.getcwd()
            defaultFile = ""
        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=defaultDir,
            defaultFile=defaultFile, wildcard=MainFrame.WILDCARD, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
            )
        if dlg.ShowModal() == wx.ID_OK:
            self.saveTransactions(dlg.GetPath())
        dlg.Destroy()

    def loadTransactions(self, file=None):
        self.ts = TransactionStore()
        if file is not None:
            self.ts.loadTransactions(file)
            self.file = file
        self.transactionManagement.ts = self.ts
        self.cashFlowDisplay.ts = self.ts
        self.updateChildren()

    def saveTransactions(self, file=None):
        if file is None:
            file = self.file
        self.file = file
        self.ts.saveTransactions(file)

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()
