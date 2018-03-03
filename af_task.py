#import Pandas
import pandas as pd

#load external data files into dataframes
GradeLevels = pd.read_csv('GradeLevels.csv')
Sites = pd.read_csv('Sites.csv')
SampleData = pd.read_excel('F&P Sample Data Set.xlsx', sheetname='Sample F&P Data')

#------------------- Functions & Prep work -------------------
#this generic function from StackExchange will rearrange columns
def change_column_order(df, col_name, index):
    cols = df.columns.tolist()
    cols.remove(col_name)
    cols.insert(index, col_name)
    return df[cols]

#clean student id
#student ids must be 9 digits, but some only have 8. 
#All with 9 digits start with 1, 
#so for the prototype I will assume that adding 1 to the front of the ID will create the correct format
def clean_id(sid):
    string_sid = str(sid)
    if(len(string_sid) == 9):
        return sid
    else:
        return int("1" + string_sid)
        
#As there are only 4 schools in our sample data, I'll create a dictionary manually.
sitesDict = {
    "Crown Heights Middle School" : 7,
    "Bushwick Middle School" : 10,
    "Bushwick MS" : 10,
    "Crown Hghts Middle School" : 7
}

#GradeID - standardize
#Only four unique data types here as well, so a simple if/else.
def checkGID(s):
    if(s == "5th"):
        return 5
    elif(s == "6th"):
        return 6
    else:
        return s

#Proficiency ID
#Works, but should be streamlined at the next pass.
def prof(gid, period, score):
    if(gid == 4):
        if(period == "EOY"):
            if(score >= 1 and score <=9):
                return 1
            elif(score > 9 and score <= 11):
                return 2
            elif(score > 11 and score <= 13):
                return 3
            elif(score >= 14):
                return 4
    elif(gid == 5):
        if(period == "BOY"):
            if(score >= 1 and score <=9):
                return 1
            elif(score > 9 and score <= 11):
                return 2
            elif(score > 11 and score <= 13):
                return 3
            elif(score >= 14):
                return 4
        elif(period == "EOY"):
            if(score >= 1 and score <=11):
                return 1
            elif(score > 11 and score <= 13):
                return 2
            elif(score > 13 and score <= 15):
                return 3
            elif(score >= 16):
                return 4  
    elif(gid == 6):
        if(period == "BOY"):
            if(score >= 1 and score <=11):
                return 1
            elif(score > 11 and score <= 13):
                return 2
            elif(score > 13 and score <= 15):
                return 3
            elif(score >= 16):
                return 4          
        elif(period == "EOY"):
            if(score >= 1 and score <=13):
                return 1
            elif(score > 13 and score <= 15):
                return 2
            elif(score > 15 and score <= 17):
                return 3
            elif(score >= 18):
                return 4
    if(gid == 7):
        if(period == "BOY"):
            if(score >= 1 and score <=13):
                return 1
            elif(score > 13 and score <= 15):
                return 2
            elif(score > 15 and score <= 17):
                return 3
            elif(score >= 18):
                return 4
            
#-----------------Build students.csv-------------
#students.csv is one of the files the vendor requires and is built to their specifications.
students = pd.DataFrame.copy(SampleData)

#reorder columns
students = change_column_order(students, 'Last',1)
students = change_column_order(students, 'First', 2)

#create column for middle name, reorder
students["MiddleName"] = ""
students = change_column_order(students, 'MiddleName', 3)

#create column for ActiveAccount.  Assuming all students are active accounts at this point.
students["ActiveAccount"] = "A"
students = change_column_order(students, 'ActiveAccount', 4)

#map the site IDs according to school name
students['SiteID'] = students['School Name'].map(sitesDict)
students = students.drop(['School Name'], axis=1)

#create the GradeID field
students['GradeID'] = students.apply(lambda row: checkGID(row[5]), axis=1)

#drop data no longer needed for submission
students = students.drop(['Grade Level', 'BOY F&P Score', 'EOY F&P Score'], axis=1)

#rename columns to match format
students = students.rename(index=str, columns = {"Student ID": "StudentID", "Last": "LastName", "First": "FirstName"})


#df.rename(index=str, columns={"A": "a", "C": "c"})
#output csv
students.to_csv('students.csv')

#-------------------Build student_scores.csv----------
#Another file output to meet vendor specifications.
#use iterrows and df.append to create the scores table

columns = ['StudentID', 'Period', 'Score', 'ProficiencyID']
ss = pd.DataFrame(columns=columns)

#for each row in the sample data, generate a BOY score, if it exists
for index, row in SampleData.iterrows():
    if(pd.notnull(row['BOY F&P Score'])):
        temp = pd.DataFrame({
            'StudentID': [row['Student ID']],
            'Period' : ['BOY'],
            'Score' : [row['BOY F&P Score']],
            'ProficiencyID' : prof(row['Grade Level'], "BOY", row['BOY F&P Score'])
        })
        ss = pd.concat([ss, temp])
        del temp
#generate a EOY score, if it exists        
    if(pd.notnull(row['EOY F&P Score'])):
        temp = pd.DataFrame({
            'StudentID': [row['Student ID']],
            'Period' : ['EOY'],
            'Score' : [row['EOY F&P Score']],
            'ProficiencyID' : prof(row['Grade Level'], "EOY", row['EOY F&P Score'])
        })
        ss = pd.concat([ss, temp])
        del temp  

ss = change_column_order(ss, 'StudentID', 0)
ss = change_column_order(ss, 'Score', 2)
        
ss.to_csv('student_scores')