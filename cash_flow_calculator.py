#!/usr/bin/env python
import wx
import wx.adv
from datetime import date, timedelta
from cash_flow.transaction import Transaction
from cash_flow.transaction_store import TransactionStore
from cash_flow.cash_flow import CashFlow


class TransactionManagement(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self.ts = TransactionStore()

        self.editPane1 = None
        self.transaction_buttons = {}

        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.left_side_sizer = wx.BoxSizer(wx.VERTICAL)
        self.t_list_sizer = wx.BoxSizer(wx.VERTICAL)

        for t in self.ts.getTransactions():
            self.updateButtonForTransaction(t)

        self.left_side_sizer.Add(self.t_list_sizer, 0)
        btn = wx.Button(self, label='New Transaction')
        btn.Bind(wx.EVT_BUTTON, self.newTransaction)
        self.left_side_sizer.Add(btn, 0)

        self.main_sizer.Add(self.left_side_sizer, 0)

        self.SetSizer(self.main_sizer)

    def clearEditPane(self):
        if self.main_sizer.GetItemCount() > 1:
            self.main_sizer.Remove(1)
            if self.editPane1:
                self.editPane1.Destroy()
                self.editPane1 = None
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
        self.t_list_sizer.Clear()
        for t in self.transaction_buttons:
            self.transaction_buttons[t].Destroy()
        self.transaction_buttons = {}
        for t in self.ts.getTransactions():
            self.updateButtonForTransaction(t)
        self.main_sizer.Layout()

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

        # Date
        label = wx.StaticText(self, label='Date', size=(50, -1))
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
        tdate = wx.DateTime(self.transaction.start.day, self.transaction.start.month-1, self.transaction.start.year)
        self.start.SetValue(tdate)
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
        wxDate = self.start.GetValue()
        new_date = date(wxDate.GetYear(), wxDate.GetMonth()+1, wxDate.GetDay())
        self.transaction.updateStartDate(new_date)
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
    def __init__(self):
        super().__init__(parent=None, title='Cash Flow Calculator')
        self.transactionManagement = TransactionManagement(self)
        self.Show()


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()
