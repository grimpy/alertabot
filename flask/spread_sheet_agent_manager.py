import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config
import datetime
from datetime import time
from calendar import  monthrange
from toml_manager import TomlManager
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

class MissingSpreadsheet(Exception):
    """
    Error when find on spreadsheet returns none
    """
    pass

@singleton
class AgentManager:
    def __init__(self):
        self.scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(config.GOOGLE_API_KEY_PATH, self.scope)
        self.shifts = {}
        self.agents = []
        self.last_updated = None
        self.update()


    def load_sheets(self):
        self.gc = gspread.authorize(self.credentials)
        self.ops_spread_sheet = self.gc.open(config.AGENTS_SHEET_NAME)
        self.devops_sheet = self.ops_spread_sheet.worksheet(config.DEVOPS_SHEET_NAME)
        self.monitoring_sheet = self.ops_spread_sheet.worksheet(config.MONITORS_SHEET_NAME)
        self.shifts_sheet = self.ops_spread_sheet.worksheet(config.SHIFTS_CODE_NAME)

    def get_current_monitors(self):
        return [agent for agent in self.agents if agent['shift'] == self.get_current_shift()]

    def get_current_first_oncalls(self):
        return [agent for agent in self.agents if agent['shift'] == 'OC-1']

    def get_current_second_oncalls(self):
        return [agent for agent in self.agents if agent['shift'] == 'OC-2']

    def update(self):
        """
        update cached agents data, basically will be called once per day
        """
        try:
            self.load_sheets()
            self.load_shifts()
            self.load_agents([self.monitoring_sheet, self.devops_sheet])
        except gspread.exceptions.CellNotFound as e :
            return 'Warning Spreadsheet does not contain %s notification will be disabled for this date.' % e.args[0]

    def load_shifts(self):
        """
        Loads shifts sheet in a dict to be easy to check current shift
        shifts = {'N': ['7:00', '12:00'], 'M':[12:00, 15:00}}
        """
        self.shifts = {}
        for i in range(2, self.shifts_sheet.col_count):
            if self.shifts_sheet.cell(2, i).value:
                self.shifts[self.shifts_sheet.cell(2, i).value] = [self.shifts_sheet.cell(3,i).value, self.shifts_sheet.cell(4,i).value]
            else:
                break

    def load_agents(self, sheets):
        """
        Loads agents for the current day only
        """
        self.agents = []
        now = datetime.datetime.now()
        date = "{}/{}".format(now.month, now.day)
        for sheet in sheets:
            date_cell = sheet.find(date)
            first_row, count = self.get_table_length(sheet, date_cell)
            for i in range(count):
                if sheet.cell(first_row+i, date_cell.col).value:
                    telegram_col = sheet.find("TelegramID").col
                    name = sheet.cell(first_row+i, telegram_col-1).value
                    telegram = sheet.cell(first_row+i, telegram_col).value.strip('@')
                    shift = sheet.cell(first_row+i, date_cell.col).value
                    self.agents.append({'name': name, 'telegram':telegram, 'shift':shift})
        self.last_updated = date

    def get_agents(self, sheets, date):
        """
        get working agents in specific date
        sheets: list of sheets to get agents from
        date : date in "month/day" to be the same as in the sheet
        """
        agents = []
        for sheet in sheets:
            date_cell = sheet.find(date)
            first_row, count = self.get_table_length(sheet, date_cell)
            for i in range(count):
                if sheet.cell(first_row+i, date_cell.col).value:
                    telegram_col = sheet.find("TelegramID").col
                    name = sheet.cell(first_row+i, telegram_col-1).value
                    telegram = sheet.cell(first_row+i, telegram_col).value.strip('@')
                    shift = sheet.cell(first_row+i, date_cell.col).value
                    agents.append({'name': name, 'telegram':telegram, 'shift':shift})
        # self.last_updated = date
        return agents


    def current_date(self):
        now = datetime.datetime.now()
        date = "{}/{}".format(now.month, now.day)
        return date

    def get_current_shift(self):
        shift = None
        now = datetime.datetime.now()
        for shift, time_list in self.shifts.items():
            start_time = list(map(int, time_list[0].split(":")))
            end_time = list(map(int, time_list[1].split(":")))
            if start_time and end_time:
                if end_time[0] > start_time[0]:
                    if time(now.hour, now.minute) > time(start_time[0], start_time[1]) and time(now.hour, now.minute) < time(end_time[0], end_time[1]):
                        break
                else:
                    if time(now.hour, now.minute) > time(start_time[0], start_time[1]) and time(now.hour, now.minute) < time(23, 59):
                        break
                    if time(now.hour, now.minute) > time(0, 0) and time(now.hour, now.minute) < time(end_time[0], end_time[1]):
                        break
        else:
            raise Exception("Current time doesn't match any shifts")
        return shift


    def get_table_length(self, sheet, date_cell):
        """
        table length will be determined by counting from the day cell for example 25/9 until
        we found a row with out a name
        """
        first_row = date_cell.row + 2 #first row in the table (data row)
        count = 0
        for i in range(first_row, sheet.row_count):
            telegram_col = sheet.find("TelegramID").col
            if sheet.cell(i,telegram_col).value: # the telegram col must be exists
                count += 1
            else:
                break
        return first_row, count

    def get_agents_for_month(self):
        """
        export the excel sheet to toml for each person for this months
        the date to be exported will start from the current day till the end of the month
        agents = {'agent_1' : {'N': [1,2,3,4,5,6,7,8]}, {'D': 22,23,24}}
        """

        agents_data = {}
        date = self.current_date()
        now = datetime.datetime.now()
        max_days = monthrange(now.year, now.month)[1]
        sheets = [self.monitoring_sheet, self.devops_sheet]
        for i in range(1, max_days + 1):
            agents = self.get_agents(sheets, "{}/{}".format(now.month, i))
            for agent in agents:
                agent_data = agents_data.get(agent['name'], {})
                shift = agent_data.get(agent['shift'], [])
                shift.append(i)
                agent_data[agent['shift']] = shift
                agents_data[agent['name']] = agent_data
        return agents_data

    def export_to_toml(self):
        toml_manager = TomlManager()
        month_agents = self.get_agents_for_month()
        for name, data in month_agents.items():
            monitoring_data = self.get_monitoring_data(data)
            toml_manager.update(name, monitoring_data)
        toml_manager.push_changes()

    def get_monitoring_data(self, agent_data):
        """
        cron = "Min Hour Day Month Weekday : valid_for"
        """
        now = datetime.datetime.now()
        max_days = monthrange(now.year, now.month)[1]
        valid_for = max_days - now.day
        crons = []
        for key, value in agent_data.items():
            if key in self.shifts.keys():
                shift_time = self.shifts[key]
                start = shift_time[0].split(":")[0] # get the hour part
                end = shift_time[1].split(":")[0]
                hour = "{}-{}".format(start, end)
                role = "Monitor"
            else:
                hour = "*"
                role = "On Call"
            days = ",".join([str(x) for x in value])
            cron = "* {hour} {days} {month} *:{valid_for}d".format(hour=hour, days=days, month=now.month, valid_for=valid_for)
            crons.append(cron)
            monitoring_data = {'monitoring': {"period": crons, "role": role}}
        return monitoring_data
