

## Download 

#### Option 1: Zip

download zip folder

#### Option 2:git clone

intall git on your computer (ubunutu)

```unix 
sudo apt-get install git
```

then clone folder wherever you want (in order to have some consistency, let's assume you do that on your Desktop)

```
mkdir ~/Desktop/Ultrasound/
cd ~/Desktop/Ultrasound
git clone ...
```

## Set-Up

if you plan on not changing the code, create also in your Ultrasound folder 2 other folders: 
- dicom_input
- dicom_output

( you then end up with 3 folder inside the Ultrasound one)

then install the required library

```unix
$ sudo apt-get install python-pip
$ cd {where is the folder}/Ultrasound/Ultrasound_did
$ sudo pip install -r requirement.txt
```

(maybe some of them evolved or are missing, apologies)


## Run 

```unix
cd /Desktop/Ultrasound/Ultrasound_did
python main.py
```
This will fill up completely the dicom_output file which is the only thing we will touch

