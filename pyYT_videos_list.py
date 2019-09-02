import execute
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import csv

class ListGenerator:
    def __init__(self, channelName):
        '''
        Creates a list generator object with one required positional argument: channelName. Example usage:
            LG = ListGenerator('theChannelYouWantToScrape')
        '''
        self.channelName = channelName
    
    def generate_list(self, csv=True, txt=True, docx=False, headless=False, scroll_pause_time=0.8, writeFormat='x'):
        '''
        The generate_list method has been designed to make a CSV and text file by default, open an automated browsing instance, wait 0.8 seconds between scrolls when collecting video information from the provided channelName for the ListGenerator instance, and opens the designated CSV/text/docx file in  exclusive creation mode - meaning the write operation fails if the file already exists.
        
        If you DON'T want to open the automated browsing instance and prefer to run the program in headless mode, run the method with headless set to True:
            LG.generate_list(headless=True)
        
        If you do not want to write to specific file types, include the optional parameter in the method call and set it equal to false. For instance:
            LG.generate_list(csv=False)
            LG.generate_list(txt=False)
        
        If you think the file generated by this function is not including all the videos for the channelName you provided, run the method with headless mode set to False and see if the browsing instance is ending prematurely (could be due to long buffer period, low bandwidth, etc.):
            LG.generate_list(headless=False)
            
        If the browsing instance is actually ending prematurely because the browser does not find any new videos loaded in the default pause time of 0.8 seconds, try increasing the scroll_pause_time to a progressively larger number until the automated browsing instance captures all the videos for the channelName you provided (probably most helpful if used with headless disabled):
            LG.generate_list(headless=False, scroll_pause_time=1.1)
            
        If you want to overwrite an existing file of the same name, run the method with writeFormat set to 'w':
            LG.generate_list(writeFormat='w')
            
        NOTE! You can use a combination of the optional parameters (or all the optional parameters at once) in the method call, you do not need to use them one at a time. The reason it is shown one at a time here in the documentation is to highlight what each parameter does.
        '''
        
        programStart = time.perf_counter()
        if headless is False: # opens Selenium browsing instance
            driver = webdriver.Firefox()
            print ('\nAdvanced usage: you can run this program in headless mode with the optional "headless" parameter set to True to speed up execution slightly:')
            print ('    LG.generate_list(headless=True)\n')
        else:
            options = Options()
            options.headless = True
            driver = webdriver.Firefox(options=options)
        with driver:
            videosList = execute.scrollToBottom(self.channelName, driver, scroll_pause_time)
            if len(videosList) == 0:
                print ('No videos were found for the channel you provided. Are you sure you typed in the channel name correctly?')
                return
            if csv is True:
                try:
                    execute.writeToTxt(videosList, self.channelName, writeFormat)
                except FileExistsError as e:
                    print (e)
                    print ('This error indicates that a file of this name already exists in the current directory. If you want to overwrite this file, run the generate_list method again with the optional parameter "writeFormat" set to "w"')
                    print ('Example usage:\n LG.generate_list(writeFormat="w")\n')
            if txt is True:
                try:
                    execute.writeToCsv(videosList, self.channelName, writeFormat)
                except FileExistsError as e:
                    print (e)
                    print ('This error indicates that a file of this name already exists in the current directory. If you want to overwrite this file, run the generate_list method again with the optional parameter "writeFormat" set to "w"')
                    print ('Example usage:\n LG.generate_list(writeFormat="w")\n')
        programEnd = time.perf_counter()
        totalTime = programEnd - programStart
        print(f'This program took {totalTime} seconds to complete.\n')

def main():
    execute.main()
        
if __name__ == '__main__':
    main()