import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config
import datetime


def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class AgentManager:
    def __init__(self):
        self.scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(config.GOOGLE_API_KEY_PATH, scope)
        self.shifts = {}
        self.agents = []
        self.last_update = None


    def load_sheets(self):
        self.gc = gspread.authorize(credentials)
        self.ops_spread_sheet = gc.open(config.DEVOPS_SHEET_KEY)
        self.devops_sheet = ops_spread_sheet.worksheet(config.DEVOPS_SHEET_NAME)
        self.monitoring_sheet = ops_spread_sheet.worksheet(config.MONITORS_SHEET_NAME)
        self.shifts_sheet = ops_spread_sheet.worksheet(config.SHIFTS_CODE_NAME)

    def get_current_monitors(self):
        return [agent for agent in self.agents if agent['shift'] == get_current_shift()]

    def get_current_first_oncalls(self):
        return [agent for agent in self.agents if agent['shift'] == 'OC-1']

    def get_current_second_oncalls(self):
        return [agent for agent in self.agents if agent['shift'] == 'OC-2']

    def update(self):
        """
        update cached agents data, basically will be called once per day
        """
        self.load_sheets()
        self.load_shifts()
        self.load_agents([self.monitoring_sheet, self.devops_sheet])

    def load_shifts():
        """
        Loads shifts sheet in a dict to be easy to check current shift
        shifts = {'N': ['7:00', '12:00'], 'M':[12:00, 15:00}}
        """
        self.shifts = {}
        for i in range(2, shifts_sheet.col_count):
            if shifts_sheet.cell(2, i).value:
                self.shifts[shifts_sheet.cell(2, i).value] = [shits_sheet.cell(3,i), shifts_sheet.cell(4,i)]
            else:
                break

    def load_agents(self, sheets):
        """
        Loads agents for the current day only
        """
        self.agents = []
        now = datetime.datetime.now()
        date = "{}/{}".format(now.moth, now.day)
        date_cell = sheet.find(date)
        for sheet in sheets
            first_row, count = get_table_length(sheet, date_cell)
            for i in range(count):
                if sheet.cell(first_row+i, date_cell.col).value:
                    name = sheet.cell(first_row+i, 2)
                    telegram = sheet.cell(first_row+i, 3)
                    shift = sheet.cell(first_row+1, date_cell.col).value
                    self.agents.append({'name': name, 'telegram':telegram, 'shift':shift})
        self.last_updated = date

    def get_current_shift(self):
        shift = None
        now = datetime.datetime.now()
        for shift, time_list in self.shifts:
            start_time = time_list[0].split(":")
            end_time = time_list[1].split(":")
            if start_time and end_time:
                if time(now.hour, now.minute) > time(start_time[0], start_time[1]) and time(now.hour, now.minute) < time(end_time[0], end_time[1]):
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
        for i in range(first_row, aa.row_count):
            if aa.cell(i,2).value: # the col(2) is the name column which should be exists
                count += 1
            else:
                break
        return first_row, count
