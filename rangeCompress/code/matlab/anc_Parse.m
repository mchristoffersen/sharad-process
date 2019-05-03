function [ t_anc ] = anc_Parse( sci_file_name,length,width,anc_output_name )
%function [ t_anc ] = sciancparse( anc_file_name, length, width, anc_output_name )
%   Parse the ancillary data in SHARAD science files
%   Michael Christoffersen
%   April 2016
%   Parses the ancillary data in SHARAD science files according to the format
%   specified in:
%   http://pds-geosciences.wustl.edu/mro/mro-m-sharad-3-edr-v1/mrosh_0003/label/science_ancillary.fmt

%Variables
%anc_file_name = './rawdata/e_0592101_001_ss19_700_a_s.dat'; %name and path to ancillary (science) data file
%length = 24509; %how many rows to parse, max value is length of file
%width = 3786; %Width in bytes of the ancillary table 8bit=3786 6bit=2886 4bit=?
%anc_output_name = '0592101_anc_info.xls';

%% Parse SHARAD Ancillary Data

bitwidth = 8*width;

sciancdata = fopen(sci_file_name,'r','b');

SCET_BLOCK_WHOLE = fread(sciancdata,[length,1],'uint32',width-4);

fseek(sciancdata,4,'bof');
SCET_BLOCK_FRAC = fread(sciancdata, [length,1],'uint16',width-2);

fseek(sciancdata,6,'bof');
TLM_COUNTER = fread(sciancdata, [length,1],'uint32',width-4);

fseek(sciancdata,10,'bof');
FMT_LENGTH = fread(sciancdata, [length,1],'uint16',width-2);

fseek(sciancdata,12,'bof');
SPARE1 = fread(sciancdata, [length,1],'uint16',width-2);

fseek(sciancdata,14,'bof');
SCET_OST_WHOLE = fread(sciancdata, [length,1],'uint32',width-4);

fseek(sciancdata,18,'bof');
SCET_OST_FRAC = fread(sciancdata, [length,1],'uint16',width-2);

fseek(sciancdata,20,'bof');
SPARE2 = fread(sciancdata, [length,1],'uint8',width-1);

fseek(sciancdata,21,'bof');
OST_LINE_NUMBER = fread(sciancdata, [length,1],'uint8',width-1);

%Begin bit column 1 (OST LINE)

fseek(sciancdata,22,'bof');
PULSE_REPETITION_INTERVAL = fread(sciancdata, [length,1],'ubit4',bitwidth-4);

fseek(sciancdata,22,'bof');
fread(sciancdata,[1,1],'1*ubit4');
PHASE_COMPENSATION_TYPE = fread(sciancdata,[length,1],'*ubit4',bitwidth-4);

fseek(sciancdata,23,'bof');
SPARE3 = fread(sciancdata, [length,1],'ubit2',bitwidth-2);

fseek(sciancdata,23,'bof');
fread(sciancdata,[1,1],'1*ubit2');
DATA_TAKE_LENGTH = fread(sciancdata, [length,1],'ubit22',bitwidth-22);
 
fseek(sciancdata,26,'bof');
OPERATIVE_MODE = fread(sciancdata, [length,1],'ubit8',bitwidth-8);

fseek(sciancdata,27,'bof');
MANUAL_GAIN_CONTROL = fread(sciancdata, [length,1],'ubit8',bitwidth-8);
 
fseek(sciancdata,28,'bof');
COMPRESSION_SELECTION = fread(sciancdata, [length,1],'ubit1',bitwidth-1);

fseek(sciancdata,28,'bof');
fread(sciancdata,[1,1],'1*bit1');
CLOSED_LOOP_TRACKING = fread(sciancdata, [length,1],'ubit1',bitwidth-1);

fseek(sciancdata,28,'bof');
fread(sciancdata,[1,2],'2*bit1');
TRACKING_DATA_STORAGE = fread(sciancdata, [length,1],'ubit1',bitwidth-1);

fseek(sciancdata,28,'bof');
fread(sciancdata,[1,3],'3*bit1');
TRACKING_PRE_SUMMING = fread(sciancdata, [length,1],'ubit3',bitwidth-3);

fseek(sciancdata,28,'bof');
fread(sciancdata,[1,6],'6*bit1');
TRACKING_LOGIC_SELECTION = fread(sciancdata, [length,1],'ubit1',bitwidth-1);

fseek(sciancdata,28,'bof');
fread(sciancdata,[1,7],'7*bit1');
THRESHOLD_LOGIC_SELECTION = fread(sciancdata, [length,1],'ubit1',bitwidth-1);

fseek(sciancdata,29,'bof');
SAMPLE_NUMBER = fread(sciancdata, [length,1],'ubit4',bitwidth-4);

fseek(sciancdata,29,'bof');
fread(sciancdata,[1,4],'4*bit1');
SPARE4 = fread(sciancdata, [length,1],'ubit1',bitwidth-1);

fseek(sciancdata,29,'bof');
fread(sciancdata,[1,5],'5*bit1');
ALPHA_BETA = fread(sciancdata, [length,1],'ubit2',bitwidth-2);

fseek(sciancdata,29,'bof');
fread(sciancdata,[1,7],'7*bit1');
REFERENCE_BIT = fread(sciancdata, [length,1],'ubit1',bitwidth-1);

fseek(sciancdata,30,'bof');
THRESHOLD = fread(sciancdata, [length,1],'ubit8',bitwidth-8);

fseek(sciancdata,31,'bof');
THRESHOLD_INCREMENT = fread(sciancdata, [length,1],'ubit8',bitwidth-8);

fseek(sciancdata,32,'bof');
SPARE5 = fread(sciancdata, [length,1],'ubit4',bitwidth-4);
 
fseek(sciancdata,32,'bof');
fread(sciancdata,[1,4],'4*bit1');
INITIAL_ECHO_VALUE = fread(sciancdata, [length,1],'ubit3',bitwidth-3);
 
fseek(sciancdata,32,'bof');
fread(sciancdata,[1,7],'7*bit1');
EXPECTED_ECHO_SHIFT = fread(sciancdata, [length,1],'ubit3',bitwidth-3);

fseek(sciancdata,33,'bof');
fread(sciancdata,[1,2],'2*bit1');
WINDOW_LEFT_SHIFT = fread(sciancdata, [length,1],'ubit3',bitwidth-3);

fseek(sciancdata,33,'bof');
fread(sciancdata,[1,5],'5*bit1');
WINDOW_RIGHT_SHIFT = fread(sciancdata, [length,1],'ubit3',bitwidth-3);

fseek(sciancdata,34,'bof');
SPARE6 = fread(sciancdata, [length,1],'ubit32',bitwidth-32);

%End bit column 1

fseek(sciancdata,38,'bof');
SPARE7 = fread(sciancdata, [length,1],'uint8',width-1);

fseek(sciancdata,39,'bof');
DATA_BLOCK_ID = fread(sciancdata, [length,1],'ubit24',bitwidth-24);

fseek(sciancdata,42,'bof');
SCIENCE_DATA_SOURCE_COUNTER = fread(sciancdata, [length,1],'uint16',width-2);

%Begin bit column 2 (PACKET SEGMENTATION AND FPGA STATUS)

fseek(sciancdata,44,'bof');
SCIENTIFIC_DATA_TYPE = fread(sciancdata, [length,1],'ubit1',bitwidth-1);

fseek(sciancdata,44,'bof');
fread(sciancdata,[1,1],'1*ubit1');
SEGMENTATION_FLAG = fread(sciancdata, [length,1],'ubit2',bitwidth-2);

fseek(sciancdata,44,'bof');
fread(sciancdata,[1,3],'3*ubit1');
SPARE7 = fread(sciancdata, [length,1],'ubit5',bitwidth-5);

fseek(sciancdata,45,'bof');
SPARE8 = fread(sciancdata, [length,1],'ubit4',bitwidth-4);

fseek(sciancdata,45,'bof');
fread(sciancdata,[1,4],'4*ubit1');
DMA_ERROR = fread(sciancdata, [length,1],'ubit1',bitwidth-1);

fseek(sciancdata,45,'bof');
fread(sciancdata,[1,5],'5*ubit1');
TC_OVERRUN = fread(sciancdata, [length,1],'ubit1',bitwidth-1);

fseek(sciancdata,45,'bof');
fread(sciancdata,[1,6],'6*ubit1');
FIFO_FULL = fread(sciancdata, [length,1],'ubit1',bitwidth-1);

fseek(sciancdata,45,'bof');
fread(sciancdata,[1,7],'7*ubit1');
TEST = fread(sciancdata, [length,1],'ubit1',bitwidth-1);

%End bit column 2

fseek(sciancdata,46,'bof');
SPARE9 = fread(sciancdata, [length,1],'uint8',width-1);

fseek(sciancdata,47,'bof');
DATA_BLOCK_FIRST_PRI = fread(sciancdata, [length,1],'ubit24',width-3);

fseek(sciancdata,50,'bof');
TIME_DATA_BLOCK_WHOLE = fread(sciancdata, [length,1],'uint32',width-4);

fseek(sciancdata,54,'bof');
TIME_DATA_BLOCK_FRAC = fread(sciancdata, [length,1],'uint16',width-2);

fseek(sciancdata,56,'bof');
SDI_BIT_FIELD = fread(sciancdata, [length,1],'uint16',width-2);

fseek(sciancdata,58,'bof');
TIME_N = fread(sciancdata, [length,1],'real*4',width-4);

fseek(sciancdata,62,'bof');
RADIUS_N = fread(sciancdata, [length,1],'real*4',width-4);

fseek(sciancdata,66,'bof');
TANGENTIAL_VELOCITY_N = fread(sciancdata, [length,1],'real*4',width-4);

fseek(sciancdata,70,'bof');
RADIAL_VELOCITY_N = fread(sciancdata, [length,1],'real*4',width-4);

fseek(sciancdata,74,'bof');
TLP = fread(sciancdata, [length,1],'real*4',width-4);

fseek(sciancdata,78,'bof');
TIME_WPF = fread(sciancdata, [length,1],'real*4',width-4);

fseek(sciancdata,82,'bof');
DELTA_TIME = fread(sciancdata, [length,1],'real*4',width-4);

fseek(sciancdata,86,'bof');
TLP_INTERPOLATE = fread(sciancdata, [length,1],'real*4',width-4);

fseek(sciancdata,90,'bof');
RADIUS_INTERPOLATE = fread(sciancdata, [length,1],'real*4',width-4);

fseek(sciancdata,94,'bof');
TANGENTIAL_VELOCITY_INTERPOLATE = fread(sciancdata, [length,1],'real*4',width-4);

fseek(sciancdata,98,'bof');
RADIAL_VELOCITY_INTERPOLATE = fread(sciancdata, [length,1],'real*4',width-4);

fseek(sciancdata,102,'bof');
END_TLP = fread(sciancdata, [length,1],'real*4',width-4);

fseek(sciancdata,106,'bof');
S_COEFFS = fread(sciancdata, [length,8],'8*real*4',width-32);

fseek(sciancdata,138,'bof');
C_COEFFS = fread(sciancdata, [length,7],'7*real*4',width-28);

fseek(sciancdata,166,'bof');
SLOPE = fread(sciancdata, [length,1],'real*4',width-4);

fseek(sciancdata,170,'bof');
TOPOGRAPHY = fread(sciancdata, [length,1],'real*4',width-4);

fseek(sciancdata,174,'bof');
PHASE_COMPENSATION_STEP = fread(sciancdata, [length,1],'real*4',width-4);

fseek(sciancdata,178,'bof');
RECIEVE_WINDOW_OPENING_TIME = fread(sciancdata, [length,1],'single',width-4);

fseek(sciancdata,182,'bof');
RECIEVE_WINDOW_POSITION = fread(sciancdata, [length,1],'uint32',width-4);

fclose(sciancdata);

t_anc = table(SCET_BLOCK_WHOLE,SCET_BLOCK_FRAC,TLM_COUNTER,FMT_LENGTH,SPARE1,SCET_OST_WHOLE,SCET_OST_FRAC,SPARE2,OST_LINE_NUMBER,PULSE_REPETITION_INTERVAL,PHASE_COMPENSATION_TYPE,SPARE3,DATA_TAKE_LENGTH,OPERATIVE_MODE,MANUAL_GAIN_CONTROL,COMPRESSION_SELECTION,CLOSED_LOOP_TRACKING,TRACKING_DATA_STORAGE,TRACKING_PRE_SUMMING,TRACKING_LOGIC_SELECTION,SAMPLE_NUMBER,SPARE4,ALPHA_BETA,REFERENCE_BIT,THRESHOLD,THRESHOLD_INCREMENT,SPARE5,INITIAL_ECHO_VALUE,EXPECTED_ECHO_SHIFT,WINDOW_LEFT_SHIFT,WINDOW_RIGHT_SHIFT,SPARE6,DATA_BLOCK_ID,SCIENCE_DATA_SOURCE_COUNTER,SCIENTIFIC_DATA_TYPE,SEGMENTATION_FLAG,SPARE7,SPARE8,DMA_ERROR,TC_OVERRUN,FIFO_FULL,TEST,SPARE9,DATA_BLOCK_FIRST_PRI,TIME_DATA_BLOCK_WHOLE,TIME_DATA_BLOCK_FRAC,SDI_BIT_FIELD,TIME_N,RADIUS_N,TANGENTIAL_VELOCITY_N,RADIAL_VELOCITY_N,TLP,TIME_WPF,DELTA_TIME,TLP_INTERPOLATE,RADIUS_INTERPOLATE,TANGENTIAL_VELOCITY_INTERPOLATE,RADIAL_VELOCITY_INTERPOLATE,END_TLP,S_COEFFS,C_COEFFS,SLOPE,TOPOGRAPHY,PHASE_COMPENSATION_STEP,RECIEVE_WINDOW_OPENING_TIME,RECIEVE_WINDOW_POSITION);

writetable(t_anc,anc_output_name,'WriteRowNames',true);

clear
