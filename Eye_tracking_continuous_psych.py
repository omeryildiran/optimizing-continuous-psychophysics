# optimizing continuous psychophysics experiment  code
# Omer F. Yildiran
# Start date: August 2023
# ENS-PSL LSP, Cognitice Science Masters 2nd year thesis project
# Supervisors: Guido Maiello and Pascal Mamassian
eyeFeedback=False
mouseResp=False
eyeResp=False
combinedResp=False
response_type="mouse"
if response_type=="mouse":
    mouseResp=True
elif response_type=="eye":
    eyeResp=True
elif response_type=="both":
    combinedResp=True
expectedFrameRate=60
expectedDuration=20 # in seconds

# motor noise
addMouseNoise=False

from psychopy import visual, core, event
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
from dva_to_pix import arcmin_to_px, dva_to_px,arcmin_to_dva
from numpy.random import choice as randchoice
from numpy.random import random, randint, normal, shuffle, choice as randchoice
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, iohub, hardware

from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
import sys  # to get file system encoding

from create_conditions import condition_creater, create_conditions
from psychopy import prefs
from audio_cue import create_stereo_sound, positional_audio
#from psychopy import microphone
from psychopy import visual, core, event
#from psychopy.sound import Sound
prefs.hardware['audioLib'] = ['pygame']
from psychopy.hardware import keyboard
import psychopy.iohub as io
from psychopy.iohub.util import hideWindow, showWindow
from psychopy.tools.monitorunittools import deg2pix, pix2deg
from psychopy import monitors
from NoiseGenerator import NoiseGenerator
import numpy as np

"""          Experiment INFO Setup"""
# Store info about the experiment session
psychopyVersion = '2022.2.4'
expName = 'continous_psych'  # from the Builder filename that created this script
expInfo = {
    'participant': f"{randint(0, 999999):06.0f}",
    'session': '001',
}
# --- Show participant info dialog --
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName
expInfo['psychopyVersion'] = psychopyVersion
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = _thisDir + os.sep + u'data/%s_%s_%s_%s' % (expInfo['participant'],response_type, expName, expInfo['date'],)
conditions= create_conditions(numOfBlocks=1, blob_widths=[11,17,25], repeats=5)
#setup screen properties

monitor_options = {
    "asusZenbook14": {
        "sizeIs": 1024,
        "screen_width": 15,
        "screen_height": 15,
        "screen_distance": 60
    },
    "labMon": {
        "sizeIs": 1024,
        "screen_width": 28,
        "screen_height": 28,
        "screen_distance": 60
    }
}
monitorSpecs=monitor_options["asusZenbook14"]
sizeIs=monitorSpecs["sizeIs"] # 1024
screen_width=monitorSpecs["screen_width"] #31 asuSs 14 # actual size of my screen in cm is 28x17
screen_height=monitorSpecs["screen_height"] #28 # 16.5 asus
screen_distance=monitorSpecs["screen_distance"] #60 # 57 asus
# define monitor
labMonitor=monitors.Monitor('labMon', width=37, distance=57)
labMonitor.setSizePix((sizeIs, sizeIs))
myMon=monitors.Monitor('asusMon', width=31, distance=57)
myMon.setSizePix((sizeIs, sizeIs))
#labMonitor.setgamma(2.4)
#labMonitor.setwhite([0.95, 0.95, 0.95])  # Example white point with slightly lower values
selectedMon=myMon
win = visual.Window(size=(sizeIs,sizeIs),
                     fullscr=True, 
                     monitor=myMon , 
                    units='pix', 
                    color=[0, 0, 0],
                      useFBO=True,
                      screen=1,
                      colorSpace='rgb')
field_size=[sizeIs,sizeIs]
### Set the monitor to the correct distance and size
#win.monitor.setSizePix(field_size)
win.monitor.setWidth(screen_width)
win.monitor.setDistance(screen_distance)

frameRate=win.getActualFrameRate()
print(frameRate)
expInfo['frameRate']=frameRate
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess
space2pass=keyboard.Keyboard()
endExpNow = False  # flag for 'escape' or other condition => quit the exp
mouse = event.Mouse(win=win,visible=False)
frameTolerance = 0.001  # how close to onset before 'same' frame


# Eye tracker to use ('mouse', 'eyelink', 'gazepoint', or 'tobii')
if response_type=="mouse":
    TRACKER = 'mouse'
else:
    TRACKER = 'eyelink'
BACKGROUND_COLOR = [0, 0, 0]
devices_config = dict()
eyetracker_config = dict(name='tracker')
if TRACKER == 'mouse':
    eyetracker_config['calibration'] = dict(screen_background_color=BACKGROUND_COLOR,
                                            auto_pace=True,
                                            target_attributes=dict(animate=dict(enable=True, expansion_ratio=1.5,
                                                                                contract_only=False))
                                            )
    devices_config['eyetracker.hw.mouse.EyeTracker'] = eyetracker_config
elif TRACKER == 'eyelink':
    eyetracker_config['model_name'] = 'EYELINK 1000 DESKTOP'
    eyetracker_config['simulation_mode'] = False
    eyetracker_config['runtime_settings'] = dict(sampling_rate=2000, track_eyes='RIGHT')
    eyetracker_config['calibration'] = dict(screen_background_color=BACKGROUND_COLOR, auto_pace=True)
    devices_config['eyetracker.hw.sr_research.eyelink.EyeTracker'] = eyetracker_config
else:
    print("{} is not a valid TRACKER name; please use 'mouse', 'eyelink', 'gazepoint', or 'tobii'.".format(TRACKER))
    core.quit()

ioSession = '1'
if 'session' in expInfo:
    ioSession = str(expInfo['session'])

#ioServer = io.launchHubServer(window=win, **ioConfig)
ioServer = io.launchHubServer(window=win, **devices_config)

eyetracker = ioServer.getDevice('tracker')
# create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard(backend='iohub')
# Display calibration gfx window and run calibration.
if combinedResp or eyeResp:
    result = eyetracker.runSetupProcedure()
    print("Calibration returned: ", result)


calibrationTarget = visual.TargetStim(win, 
    name='calibrationTarget',
    radius=0.01, fillColor='', borderColor='black', lineWidth=2.0,
    innerRadius=0.0035, innerFillColor='green', innerBorderColor='black', innerLineWidth=2.0,
    colorSpace='rgb', units='height'
)

# define parameters for calibration
calibration = hardware.eyetracker.EyetrackerCalibration(win, 
    eyetracker, calibrationTarget,
    units=None, colorSpace='rgb',
    progressMode='time', targetDur=1.5, expandScale=1.5,
    targetLayout='NINE_POINTS', randomisePos=True, textColor='white',
    movementAnimation=True, targetDelay=1.0
)

########################################################################################################################
### -------Initialize componens  for target tracking trial-------------------------
"""                 NOISE BACKGROUND           """
# Background noise
# Noise properties
noise_size = field_size  # Use the window size for noise texture
noise_arcmin = 11  # Standard deviation for pixel noise || noise intensity Adjust to control noise intensity
noise_std =deg2pix(degrees=arcmin_to_dva(noise_arcmin),monitor=win.monitor) #arcmin_to_px(noise_arcmin,h=screen_height,d=screen_distance,r=field_size[0])# convert arcmin to std for Gaussian
noiseQuantity=120
"""             Welcome screen to give instructions to the participant         """
# Welcome screen
welcomeText="""
Welcome to the experiment your aim is to 
follow the blob with your mouse.
In the beginning of each trial you will see a fixation cross
Then you will see a blob moving around the screen
You will be asked to follow the blob with your mouse 
"""
welcomeText = visual.TextStim(win, text=welcomeText,
                              color=[1, 1, 1], units='pix', height=20)
welcomeText.draw()
win.flip()
noise_gen = NoiseGenerator(noise_size)
noise_obj = noise_gen.create_visual_objects(win)# Generate and draw noise objects
win.flip()
# draw a text that indicate the participant to press space to continue
pressText=visual.TextStim(win, text='Press any key to continue',
                        pos=(0, -300),
                        color='red',colorSpace='rgb',units='pix', height=20)
welcomeText.draw()
pressText.draw()
win.flip()

event.waitKeys()
win.flip()

# Brownian motion properties
blob_motion_std=arcmin_to_px(arcmin=2,h=screen_height,d=screen_distance,r=field_size[0])  # Standard deviation of Gaussian white noise velocities
# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.Clock()  # to track time remaining of each (possibly non-sl€ip) routine 


####################### Blob Generation #######################
# Blob properties
initial_blob_std= arcmin_to_px(arcmin=11,h=screen_height,d=screen_distance,r=field_size[0]) 
total_lum=1*(2*np.pi*initial_blob_std ** 2)*1 # Total luminance of blobm
def generateBlob(space_constant):
    blob_std=arcmin_to_px(arcmin=blob_width,h=screen_height,d=screen_distance,r=field_size[0])
    blob_amplitude =total_lum / (2*np.pi*blob_std ** 2) # Adjust blob amplitude to keep total blob energy constant
    y, x = np.meshgrid(np.arange(noise_size[1]), np.arange(noise_size[0]))
    blob = blob_amplitude * np.exp(-((x - noise_size[0] / 2)**2 + (y - noise_size[1] / 2)**2) / (2 * blob_std**2))
    #blob = (blob - blob.min()) / (blob.max() - blob.min())*2-1 # normalize the blob
    return blob
# create blobs for each of the conditions
blob_widths=list(set(conditions))#[11,13,17,21,25,29]
blobs=[]


for blob_width in blob_widths:
    blobs.append(np.array(generateBlob(arcmin_to_px(arcmin=blob_width,h=screen_height,d=screen_distance,r=field_size[0]))))
blobs=np.array(blobs)
blobs = (blobs - blobs.min()) / (blobs.max() - blobs.min())*2-1
# create dictionary for each blob_width
blob_dict={}
for i in range(len(blob_widths)):
    blob_dict[blob_widths[i]]=blobs[i]



expectedFrames=expectedFrameRate*expectedDuration
toleranceTrialN=300 
"""                         BLOB MOTION                """ 
# Blob motion by changing velocity on x and y axis according to the brownian motion
def generateBrownianMotion(field_size, velocity_std, duration):
    # Generate random velocity for each frame
    num_frames = int(duration * expectedFrameRate)+toleranceTrialN # add 600 frames to the duration
    velocies_x=np.random.normal(0, velocity_std, num_frames)
    velocies_y=np.random.normal(0, velocity_std, num_frames)
    # new positions = old position + velocity
    pos_x = np.cumsum(velocies_x)
    pos_y = np.cumsum(velocies_y)
    # clip positions to stay within the field
    pos_x = np.clip(pos_x, -field_size/2, field_size/2 )
    pos_y = np.clip(pos_y, -field_size/2, field_size/2 )
    return (pos_x, pos_y)
    
##            OBSERVER POINTER     
#         """
sizePointer=arcmin_to_px(arcmin=15,h=screen_height,d=screen_distance,r=field_size[0])
obs_pointer = visual.Circle(win, radius=sizePointer, fillColor='red',colorSpace='rgb', units='pix',size=0.30)
##    fixation cross for the beginning of the trial (before start of the trial )  
fixationCross=visual.TextStim(win, text='+', color=[1, 1, 1], units='pix', height=20)

# data to save
## blob data
all_blob_x = []
all_blob_y = []
### eye data
allEyeX = []
allEyeY = []
allRawGazeX = []
allRawGazeY = []
### stimulus data
all_stim_x = []
all_stim_y = []
allRawStimX = []
allRawStimY = []
### mouse data
all_mouse_x = []
all_mouse_y = []
allRawMx = []
allRawMy = []
jumped=False
looksAway=False

## --- define have a rest screen ###
trialNum=0
haveRest=False
haveRestText=visual.TextStim(win, text='Press space to continue', color=[1, 1, 1], units='pix', height=20)
haveRestNum=1
#####
sigma_trials=[]
win.setMouseVisible(False)    

# create a warning text to indicate the participant to look at the blob if they look 2dva away from the blob
redoTrialText=visual.TextStim(win, text='Did you get distracted in last trial?\n Well now you need to redo do trial or press C to recalibrate or N to just go ahead!', color=[1, 1, 1], units='pix', height=20)
redoTrial=False
calibOkText=visual.TextStim(win, text='Is Calibration done? Are you ready to continue? (Y/N)', color=[1, 1, 1], units='pix', height=20)
#conditions=sorted(conditions)
from random import shuffle
shuffle(conditions)
#region [rgba(20, 184, 196, 0.23)]
while trialNum < len(conditions) and not endExpNow:
    blob_width = conditions[trialNum]
    if redoTrial:
        redoTrialText.draw()
        win.flip()
        event.waitKeys()
        redoTrial=False
        theseKeys = event.waitKeys(keyList=['c', 'n'])
        if theseKeys:
            if 'c' in theseKeys:
                # run calibration
                calibration.run()
                defaultKeyboard.clearEvents()
                routineTimer.reset()
                calibOkText.draw()
                win.flip()
                theseKeys2=event.waitKeys(keyList=['y', 'n'])
                if 'y' in theseKeys2:
                    continue
            elif 'n' in theseKeys:
                continue
        # redo the last blob_width
        continue
    else:
        sigma_trials.append(blob_width)
    _space2pass_allKeys = []
    space2pass.keys = []
    space2pass.clearEvents(eventType='keyboard')
    #save conditions
    #if trialNum%haveRestNum==0 and trialNum!=1:
    haveRest=True
    while haveRest:
        haveRestText.draw()
        win.flip()
        theseKeys = space2pass.getKeys(keyList=['space'])
        _space2pass_allKeys.extend(theseKeys)
        if len(_space2pass_allKeys)>0:
            haveRest=False

    mouse.setPos((0,0))
    # set a timer for the next line record the time spent
    tStart = globalClock.getTime()
    # clear all drawings
    #print(blob_width)
    blob_std=arcmin_to_px(arcmin=blob_width,h=screen_height,d=screen_distance,r=field_size[0])
    # create blob
    blob=blob_dict[blob_width]
    blob_obj = visual.GratingStim(win, tex=None, mask=blob,  units='pix', interpolate=False)
    
    mouse.setPos(newPos=(0,0))
    win.flip(clearBuffer=True)
    # create blob motion positions
    pos_x_obj, pos_y_obj = generateBrownianMotion(field_size=noise_size[0], velocity_std=blob_motion_std, duration=expectedDuration)# pre-generate brownian motion
    pos_x_obj=np.insert(pos_x_obj,0,0)
    pos_y_obj=np.insert(pos_y_obj,0,0)
    # append blob positions for each trial
    all_blob_x.append(pos_x_obj)
    all_blob_y.append(pos_y_obj)

    win.clearBuffer()
    intensity_profiles = []  # List to store intensity profiles
    continueRoutine = True
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    realFrameN=-1

    routineTimer.reset()
    t = 0
    # # wait for 1 second before starting the trial
    waiterTime=0
    while  waiterTime <0.2:
        waiterTime = globalClock.getTime() - tStart
        fixationCross.draw()
        win.flip()
    # draw the stimulus
    blob_obj.setAutoDraw(True)
    mouse.setVisible(False)
    # draw observation pointer
    if mouseResp or combinedResp or eyeFeedback:
        obs_pointer.setAutoDraw(True)
    else:
        obs_pointer.setAutoDraw(False)
    # all eye responses
    eyeRespsX=np.empty((expectedFrames))
    eyeRespsY=np.empty((expectedFrames))
    # all mouse responses
    mX=np.empty((expectedFrames))
    mY=np.empty((expectedFrames))
    # all raw mouse responses
    rawMx=[]
    rawMy=[]
    # all raw gaze responses
    rawGazeX=[]
    rawGazeY=[]

    # all stimulus positions
    stim_x=np.empty((expectedFrames))
    stim_y=np.empty((expectedFrames))
    mouse_v=np.empty((expectedFrames))
    rawStimX=[]
    rawStimY=[]
    checkPointX=0
    checkPointY=0

    jumpTreshold=dva_to_px(size_in_deg=2,h=screen_height,d=screen_distance,r=field_size[0])
    print(jumpTreshold)
    looksAwayTreshold=dva_to_px(size_in_deg=5,h=screen_height,d=screen_distance,r=field_size[0])
    wrongGazePointer= visual.Circle(win, radius=10, fillColor='black',colorSpace='rgb', units='pix',size=0.30)
    #jumpTreshold=arcmin_to_px(arcmin=blob_width*10,h=screen_height,d=screen_distance,r=field_size[0])
    #looksAwayTreshold=arcmin_to_px(arcmin=blob_width*30,h=screen_height,d=screen_distance,r=field_size[0])
    #ioServer.ClearEvents()
    gXall=[0]
    gYall=[0]
    tStart = globalClock.getTime()
    #region [rgba(206, 10, 118, 0.14)]
    ##################### Trial Start #####################
    eyetracker.setRecordingState(True)  # start recording of gaze
    while continueRoutine:
        if realFrameN>len(pos_x_obj)-2:
            redoTrial=True
            break            
        realFrameN=realFrameN+1
        random_noise_index = int(randint(0, noiseQuantity))
        noise_obj[random_noise_index].draw()    # draw noise
        blob_obj.setPos((pos_x_obj[realFrameN], pos_y_obj[realFrameN]))
        rawStimX.append(pos_x_obj[realFrameN])
        rawStimY.append(pos_y_obj[realFrameN])
        #frameN+= 1  # number of completed frames (so 0 is the first frame)
        if eyeResp or combinedResp:
            # Get the latest gaze position in display coord space.
            gpos = eyetracker.getLastGazePosition()
            valid_gaze_pos = isinstance(gpos, (tuple, list))
            if valid_gaze_pos:
                gX=gpos[0]
                gY=gpos[1]
                rawGazeX.append(gX)
                rawGazeY.append(gY)
                looksAway=(np.sqrt((pos_x_obj[realFrameN]-gX)**2+(pos_y_obj[realFrameN]-gY)**2))>looksAwayTreshold
                if not looksAway:
                    gXall.append(gX)
                    gYall.append(gY)
                    jumped=np.sqrt((gX-gXall[-2])**2+(gY-gYall[-2])**2)>jumpTreshold
                    if not jumped:
                        frameN+=1
                        stim_x[frameN]=blob_obj.pos[0]
                        stim_y[frameN]=blob_obj.pos[1]
                        eyeRespsX[frameN]=gX
                        eyeRespsY[frameN]=gY
            else:
                rawGazeX.append(9999)
                rawGazeY.append(9999)
            #         elif jumped:
            #             wrongGazePointer.setPos((gX,gY))
            #             wrongGazePointer.draw()
            #     elif looksAway:
            #         wrongGazePointer.setPos((gX,gY))
            #         wrongGazePointer.draw()
            # if not valid_gaze_pos:
            #     wrongGazePointer.setPos((0,0))
            #     wrongGazePointer.draw()
            if eyeFeedback:
                obs_pointer.setPos((gX,gY))
        rawMx.append(mouse.getPos()[0])
        rawMy.append(mouse.getPos()[1])
        if combinedResp:
            obs_pointer.setPos(mouse.getPos())
            if not jumped and not looksAway or valid_gaze_pos:
                mX[frameN]=mouse.getPos()[0]
                mY[frameN]=mouse.getPos()[1]
        elif mouseResp:
            if addMouseNoise:
                obs_pointer.setPos((mouse.getPos()[0]+np.random.normal(0,2),mouse.getPos()[1]+np.random.normal(0,2)))
            else:
                obs_pointer.setPos(mouse.getPos())
            frameN+=1
            mX[frameN]=mouse.getPos()[0]
            mY[frameN]=mouse.getPos()[1]
            stim_x[frameN]=blob_obj.pos[0]
            stim_y[frameN]=blob_obj.pos[1]

        # flip the window
        win.flip()
        # end the loop after given seconds
        if frameN > expectedFrames-2:
            continueRoutine = False
        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            endExpNow = True
            continueRoutine = False
        #endregion
    # the Routine "trial" was not non-slip safe, so reset the non-slip timer
    eyetracker.setRecordingState(False)  # stop recording of gaze
    tEnd = globalClock.getTime()
    print("trial lasteD: "+str(tEnd-tStart))
    blob_obj.setAutoDraw(False)
    obs_pointer.setAutoDraw(False)
    if redoTrial == False:
        trialNum+=1
    elif redoTrial:
        continue
    t = routineTimer.getTime()
    print("time of finish: "+str(t))
    print("Maximum frame achieved "+str(frameN))
    print("Maximum realFrame achieved "+str(realFrameN))

    # save positions of target, mouse, and but first calculate velocities
    if eyeResp:
        eyeRespsX = np.array(eyeRespsX)
        eyeRespsY = np.array(eyeRespsY)
        eyeRespsX = np.insert(eyeRespsX, 0, 0)
        eyeRespsY = np.insert(eyeRespsY, 0, 0)
        allEyeX.append(eyeRespsX)
        allEyeY.append(eyeRespsY)
    elif mouseResp:
        mX = np.array(mX)
        mY = np.array(mY)
        mX = np.insert(mX, 0, 0)
        mY = np.insert(mY, 0, 0)
        all_mouse_x.append(mX)
        all_mouse_y.append(mY)
    elif combinedResp:
        mX = np.array(mX)
        mY = np.array(mY)
        mX = np.insert(mX, 0, 0)
        mY = np.insert(mY, 0, 0)
        all_mouse_x.append(mX)
        all_mouse_y.append(mY)
        eyeRespsX = np.array(eyeRespsX)
        eyeRespsY = np.array(eyeRespsY)
        eyeRespsX = np.insert(eyeRespsX, 0, 0)
        eyeRespsY = np.insert(eyeRespsY, 0, 0)
        allEyeX.append(eyeRespsX)
        allEyeY.append(eyeRespsY)

    rawStimX = np.array(rawStimX)
    rawStimY = np.array(rawStimY)
    rawStimX = np.insert(rawStimX, 0, 0)
    rawStimY = np.insert(rawStimY, 0, 0)
    allRawStimX.append(rawStimX)
    allRawStimY.append(rawStimY)

    stim_x = np.array(stim_x)
    stim_y = np.array(stim_y)
    stim_x = np.insert(stim_x, 0, 0)
    stim_y = np.insert(stim_y, 0, 0)
    all_stim_x.append(stim_x)
    all_stim_y.append(stim_y)

    rawGazeX = np.array(rawGazeX)
    rawGazeY = np.array(rawGazeY)
    rawGazeX = np.insert(rawGazeX, 0, 0)
    rawGazeY = np.insert(rawGazeY, 0, 0)
    allRawGazeX.append(rawGazeX)
    allRawGazeY.append(rawGazeY)

    rawMx = np.array(rawMx)
    rawMy = np.array(rawMy)
    rawMx = np.insert(rawMx, 0, 0)
    rawMy = np.insert(rawMy, 0, 0)
    allRawMx.append(rawMx)
    allRawMy.append(rawMy)


    space2pass.keys = None

    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        # Create an Ending Screen
        endText=visual.TextStim(win, text='Thank you for your participation', color=[1, 1, 1], units='pix', height=20)
        endText.draw()
        win.flip()
        # and wait for participant to press space
        event.waitKeys()
        win.close()
        eyetracker.setConnectionState(False)
        break
    #endregion
# Create an Ending Screen
if not endExpNow:
    endText=visual.TextStim(win, text='Thank you for your participation press any key to exit', color=[1, 1, 1], units='pix', height=20)
    endText.draw()
    win.flip()
    # and wait for participant to press space
    event.waitKeys()
    win.close()

##
# save data as mat file
import scipy.io as sio
# make conditions as numpy
conditions=np.array(conditions)
conditions=conditions.T
filename = u'data/%s_%s_%s_%s' % (expInfo['participant'], response_type,expName, expInfo['date'])
if eyeResp:
    sio.savemat(filename+'.mat', {'eyeX': allEyeX, 'eyeY': allEyeY, 'blob_x': all_stim_x, 'blob_y': all_stim_y, 'sigma': sigma_trials,'rawGazeX':allRawGazeX,'rawGazeY':allRawGazeY,'rawStimX':allRawStimX,'rawStimY':allRawStimY})
elif mouseResp:
    sio.savemat(filename+'.mat', {'mouse_x': all_mouse_x, 'mouse_y': all_mouse_y, 'blob_x': all_stim_x, 'blob_y': all_stim_y, 'sigma': sigma_trials})
elif combinedResp:
    sio.savemat(filename+'.mat', {'eyeX': allEyeX, 'eyeY': allEyeY, 'mouse_x': all_mouse_x, 'mouse_y': all_mouse_y, 'blob_x': all_stim_x, 'blob_y': all_stim_y, 'sigma': sigma_trials,'rawGazeX':allRawGazeX,'rawGazeY':allRawGazeY,'rawMouseX':allRawMx,'rawMouseY':allRawMy,'rawStimX':allRawStimX,'rawStimY':allRawStimY})

core.quit()
