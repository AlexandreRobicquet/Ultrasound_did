from deindentify import *
import shutil
import glob

def main(input_path='../dicom_input/', output_path='../dicom_output/'):
  list = os.listdir(input_path)
  for dcm in list:
    deidentify(dcm, input_path, output_path)
  
  for a in glob.glob(output_path+'*.jpg'):
    shutil.move(a,output_path+'Images/')
  for a in glob.glob(output_path+'*.dcm'):
    shutil.move(a,output_path+'dicom/')
