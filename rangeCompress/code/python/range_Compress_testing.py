# Import necessary libraries
import numpy as np
import scipy
import matplotlib.pyplot as plt
import glob, os, sys, time
from read_Lbl import lbl_Parse
from read_Aux import aux_Parse
from read_Anc import anc_Parse
from read_Chirp import open_Chirp
from plotting import rgram
from read_EDR import EDR_Parse, sci_Decompress



def main(EDRName, auxName, lblName, chirp = 'synth', presumFac = None, beta = 0):
    """
    -----------
    This python script is used to pulse compress raw SHARAD EDRs to return chirp compressed science record. Output should be complex voltage.
    This code was adapted from Matthew Perry's FrankenRDR work, along with Michael Chrostoffersen's sharad-tools. Certain packages were directly updated from their work (ie. FrankenRDR-readLBL, readAnc, readAux). 
    This code simply aims to pulse compress the raw data, without performing any other processing steps.

    github: b-tober
    Updated by: Brandon S. Tober
    Last Updated: 09Jan18
    -----------
    Example call:

    EDRName = '/media/anomalocaris/Swaps/Google_Drive/MARS/orig/edr_test/e_5050702_001_ss19_700_a_s.dat'
    auxName =  '/media/anomalocaris/Swaps/Google_Drive/MARS/orig/edr_test/e_5050702_001_ss19_700_a_a.dat'
    lblName =  '/media/anomalocaris/Swaps/Google_Drive/MARS/orig/edr_test/e_5050702_001_ss19_700_a.lbl'
    chirp = 'calib'
    presumFac = 8
    beta = 0

    main(EDRName, auxName, lblName, chirp = chirp, presumFac = presumFac)
    """
    t0 = time.time()                    #start time
    print('--------------------------------')
    print(runName)
    print('--------------------------------')

    # extract relecant information from lbl file
    print('Reading label file...')
    lblDic = lbl_Parse(lblName)
    records = lblDic['FILE_RECORDS']    # number of records in observation (traces)
    instrPresum = lblDic['INSTR_MODE_ID']['Presum']       # onboard presums
    instrMode = lblDic['INSTR_MODE_ID']['Mode']
    BitsPerSample = lblDic['INSTR_MODE_ID']['BitsPerSample']

    # toggle on to downsize for testing purposes
    records = int(records / 10)


    # presumming is just for visualization purposes
    presumCols = int(np.ceil(records/presumFac))

    # parse aux file into data frame
    auxDF = aux_Parse(auxName)

    # determine Bits per Sample
    if BitsPerSample == 4:
        recLen = 1986
    elif BitsPerSample == 6:
        recLen = 2886
    elif BitsPerSample == 8:
        recLen = 3786

    print('InstrPresum:\t' + format(instrPresum))
    print('Instrument Mode:\t' + format(instrMode))
    print('Bits Per Sample:\t' + format(BitsPerSample))
    print('Record Length:\t' + format(recLen))
    print('Number of Records:\t' + format(records))
    print('Using Kaiser window of beta value:\t' + format(beta))
    print('---- Begin Processing ----')

    # determine TX and RX temps if using Italian reference chirp
    txTemp = auxDF['TX_TEMP'][:]
    rxTemp = auxDF['RX_TEMP'][:]
	
    
    # read in reference chirp as matched filter - this should be imported in Fourier frequency domain, as complex conjugate
    if chirp == 'calib':
        refChirpMF, refChirpMF_index = open_Chirp(chirp, txTemp, rxTemp)
    else:
        refChirpMF = open_Chirp(chirp, txTemp, rxTemp)
    print('Reference chirp opened, type:\t' +  format(chirp))

    # read in raw science data and ancil data
    sci, ancil = EDR_Parse(EDRName, records, recLen, BitsPerSample)
    print('EDR Science Data Parsed')

    # parse ancilliary data
    ancil = anc_Parse(ancil, records)
    print('Ancilliary Data Parsed')

    # decompress science data
    sci = sci_Decompress(sci, lblDic['COMPRESSION'], instrPresum, BitsPerSample, ancil['SDI_BIT_FIELD'][:])
    print('EDR Science Data Decompressed')

    # all data imported and decompressed
    # set up empty data arrays to hold Output and kaiser window of specified beta value
    if chirp =='ideal' or chirp == 'synth' or chirp == 'UPB':
        EDRData = np.zeros((3600,records), complex)
        EDRData_presum = np.zeros((3600, presumCols), complex)   
        window = np.kaiser(3600, beta)

    elif chirp == 'calib':
        EDRData = np.zeros((2048,records), complex)
        EDRData_presum = np.zeros((2048, presumCols), complex)   
        window = np.kaiser(2048,beta)     

        EDRData2 = np.zeros((4096,records), complex)
        EDRData2_presum = np.zeros((4096, presumCols), complex)   
        window2 = np.pad(np.kaiser(2048,beta),(0,4096 - refChirpMF.shape[1]),'constant')

        EDRData3 = np.zeros((4096,records), complex)
        EDRData3_presum = np.zeros((4096, presumCols), complex)   
        window3 = np.pad(np.kaiser(2048,beta),(0,4096 - refChirpMF.shape[1]),'constant')

        EDRData4 = np.zeros((4096,records), complex)
        EDRData4_presum = np.zeros((4096, presumCols), complex)   
        window4 = np.pad(np.kaiser(2048,beta),(0,4096 - refChirpMF.shape[1]),'constant')   

    geomData = np.zeros((records,5))

    #-------------------
    # setup complete; begin range compression
    #------------------- 

    if chirp =='calib':
        fc = ((80./3.) - 20.)*1e6                                                                   # 6.66 MHz - fc defined by PDS documentation     
        dt = (3./80.)*1e-6                                                                          # 0.0375 Microseconds
        t = np.arange(0*dt, 4096*dt, dt)
        phase_shift = np.exp(2*np.pi*1j*fc*t)                                                       # shift spectrum when multiplied by zero padded raw data
        refChirpMF_pad = np.pad(refChirpMF,[(0,0),(0,2049 - refChirpMF.shape[1])], 'constant')      # zeros pad reference chirp to length 2049 prior to range compression to account for missing sample in fourier spectra
        refChirpMF_padx = np.pad(refChirpMF,[(0,0),(0,4096 - refChirpMF.shape[1])], 'constant')      # zeros pad reference chirp to length 4096 prior to range compression to account for missing sample in fourier spectra
        sciPad = np.pad(sci,[(0,4096 - sci.shape[0]),(0,0)],'constant')                             # zero-pad science data to length of 4096

        for _i in range(records):
            #-------------------
            # PDS documented range compression steps -EDRData
            #-------------------
            sciShift = sciPad[:,_i] * phase_shift
            sciFFT = np.fft.fft(sciShift) #/ len(sciShift)                                          # Matt has his code set up to scale by length array
            # take central 2048 samples
            st = 1024
            en = 3072
            sciFFT_cut = sciFFT[st:en]
            # perform chirp compression
            dechirpData = (sciFFT_cut * refChirpMF[refChirpMF_index[_i],:]) #* window
            # Inverse Fourier transfrom and fix scaling
            EDRData[:,_i] = np.fft.ifft(dechirpData) #* len(dechirpData)
            #-------------------
            # revised PDS method - EDRData2
            #-------------------
            sciShift = sciPad[:,_i] * phase_shift
            sciFFT2 = np.fft.fft(sciShift) #/ len(sciShift2)                                        # Matt has his code set up to scale by length array
            # take central 2049 samples
            st2 = 1024
            en2 = 3073
            sciFFT_cut2 = sciFFT2[st2:en2]
            # perform chirp compression
            dechirpData2 = (sciFFT_cut2 * refChirpMF_pad[refChirpMF_index[_i],:]) #* window2
            dechirpData2 = np.pad(dechirpData2,(0,4096 - dechirpData2.shape[0]),'constant')         # zero-pad output data to length of 409
            # Inverse Fourier transfrom and fix scaling
            EDRData2[:,_i] = np.fft.ifft(dechirpData2) #* len(dechirpData2)
            #-------------------
            # alternative method - EDRData3
            #-------------------
            sciFFT3 = np.fft.fft(sciPad[:,_i]) #/ len(sciShift3)                                    # Matt has his code set up to scale by length array
            # take the first 2049 samples
            sciFFT3_cut = sciFFT3[:2049]
            dechirpData3 = (sciFFT3_cut * refChirpMF_pad[refChirpMF_index[_i],:]) #* window3
            dechirpData3 = np.pad(dechirpData3,(0,4096 - dechirpData3.shape[0]),'constant')         # zero-pad output data to length of 4096
            EDRData3[:,_i] = np.fft.ifft(dechirpData3) #* len(dechirpData3)
            #-------------------
            # another alternative method - EDRData4 - using reference chirp zero padded to 4096
            #-------------------
            sciFFT4 = np.fft.fft(sciPad[:,_i]) #/ len(sciShift3)                                    # Matt has his code set up to scale by length array
            dechirpData4 = (sciFFT4 * refChirpMF_padx[refChirpMF_index[_i],:]) #* window4
            EDRData4[:,_i] = np.fft.ifft(dechirpData4)#  * len(dechirpData4)

        
        #truncate revised and alternate range compressed vector to 3600
        EDRData2 = EDRData2[:3600,:]        
        EDRData3 = EDRData3[:3600,:]
        EDRData4 = EDRData4[:3600,:]

        print(EDRData.shape,EDRData2.shape,EDRData3.shape, EDRData4.shape)

    else:
        for _i in range(records):
            # fourier transform of data
            sciFFT = np.fft.fft(sci[:,_i])# / len(sci[:,_i])
            
            # multiple Fourier transform of reference chip by that of the data
            dechirpData = (sciFFT * refChirpMF) * window

            # inverse fourier transform of dechirped data to place back in time domain
            EDRData[:,_i] = np.fft.ifft(dechirpData)# * len(sci[:,_i])
    print('Range compression complete')

    # presum data by factor or eight for visualization purposes
    # for _i in range(presumCols - 1):
    #     EDRData_presum[:,_i] = np.mean(EDRData[:,presumFac*_i:presumFac*(_i+1)], axis = 1)

    # # account for traces left if number of traces is not divisible by presumFac
    # EDRData_presum[:,-1] = np.mean(EDRData[:,presumFac*(_i+1):-1], axis = 1)
    # print('Presumming complete')

    # create geom array with relavant data for each record
    for _i in range(records):
        geomData[_i,0] = runName.split('_')[1] + runName.split('_')[2]
        geomData[_i,1] = int(_i)
        geomData[_i,2] = auxDF['SUB_SC_PLANETOCENTRIC_LATITUDE'][_i]
        geomData[_i,3] = auxDF['SUB_SC_EAST_LONGITUDE'][_i]
        geomData[_i,4] = auxDF['SOLAR_ZENITH_ANGLE'][_i]

    # convert complex-valued voltage return to power values
    BruceData = np.fromfile('../../../../../orig/supl/SHARAD/EDR/EDR_pc_bruce/592101000_1_Unif_SLC.raw', dtype = 'complex64')
    BruceData = BruceData.reshape(3600, int(len(BruceData)/3600))
    BruceAmp = np.abs(BruceData)

    ampOut = np.abs(EDRData)

    # plot outputs for different methods while comparing range compression options
    if chirp =='calib':
        ampOut2 = np.abs(EDRData2)
        ampOut3 = np.abs(EDRData3)
        ampOut4 = np.abs(EDRData4)

        print(BruceAmp)
        print(ampOut4)

        plt.subplot(4,1,1)
        plt.plot(ampOut[:,int(records/2)])
        plt.title('original PDS method')
        plt.subplot(4,1,2)
        plt.plot(ampOut2[:,int(records/2)])
        plt.title('revised PDS method')
        plt.subplot(4,1,3)
        plt.plot(ampOut3[:,int(records/2)])
        plt.title('alternative method')
        plt.subplot(4,1,4)
        plt.plot(ampOut4[:,int(records/2)])
        plt.title('alternate-alternative method')
        plt.xlabel('sample')
        plt.ylabel('amplitude')
        plt.show()
    else:
        plt.subplot(2,1,1)
        plt.plot(ampOut[:,int(records/2)])
        plt.subplot(2,1,2)
        plt.plot(BruceAmp[:,int(records/2)])
        plt.show()

    # sys.exit()

    # create radargrams from presummed data to ../../orig/supl/SHARAD/EDR/EDR_pc_brucevisualize output, also save data
    # rgram(EDRData3, data_path, runName + '_' + chirp, rel = True)
    # np.savetxt(data_path + 'processed/data/geom/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_geom.csv', geomData, delimiter = ',', newline = '\n',fmt = '%s')
    # np.save(data_path + 'processed/data/rgram/comp/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_' + windowName + '_SLC_comp.npy', EDRData)
    # np.save(data_path + 'processed/data/rgram/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_' + windowName + '_SLC_amp.npy', ampOut)

    t1 = time.time()    # End time
    print('--------------------------------')
    print('Total Runtime: ' + str(round((t1 - t0),4)) + ' seconds')
    print('--------------------------------')
    return

if __name__ == '__main__':
    data_path = '/MARS/orig/supl/SHARAD/EDR/edr_test/'
    if os.getcwd().split('/')[1] == 'media':
        data_path = '/media/anomalocaris/Swaps' + data_path
    elif os.getcwd().split('/')[1] == 'mnt':
        data_path = '/mnt/d' + data_path
    else:
        print('Data path not found')
        sys.exit()
    lbl_file = sys.argv[1]
    lblName = data_path + lbl_file
    runName = lbl_file.rstrip('_a.lbl')
    auxName = data_path + runName + '_a_a.dat'
    EDRName = data_path + runName + '_a_s.dat'
    chirp = 'calib'
    presumFac = 8           # presum factor for radargram visualization; actual data is not presummed
    beta = 0                # beta value for kaiser window [0 = rectangular, 5 	Similar to a Hamming, 6	Similar to a Hann, 8.6 	Similar to a Blackman]
    if beta == 0:
        windowName = 'Unif'
    elif beta == 5:
        windowName = 'Hamming'
    elif bea == 6:
        windowName = 'Hann'
    elif beta == 8.6:
        windowName = 'Blackman'
    else:
        print('Unknown window type')
        sys.exit()
    #if (not os.path.isfile(data_path + 'processed/data/geom/' + runName + '_geom.csv')):
    main(EDRName, auxName, lblName, chirp = chirp, presumFac = presumFac, beta = beta)
    # for file in os.listdir(data_path):
    #     if file.endswith('.lbl'):
    #         lbl_file = file
    #         lblName = data_path + lbl_file
    #         runName = lbl_file.rstrip('_a.lbl')
    #         auxName = data_path + runName + '_a_a.dat'
    #         EDRName = data_path + runName + '_a_s.dat'
    #         main(EDRName, auxName, lblName, chirp = chirp, presumFac = presumFac)
    #else :
    #    print('\n' + runName.split('_')[1] + runName.split('_')[2] + ' already processed!\n')
