import json
import sys

def json_to_csv(json_path, output_path):
    csvstr= ''
    with open(json_path, 'r') as ifile:
        data = json.load(ifile)
        if len(data)>0:
            startdate = data[0]['timestamp']
            csvstr += 'Minutes,Torq (N-m),Km/h,Watts,Km,Cadence,Hrate,ID\n'
            for sensorValue in data:
                minutes = (sensorValue['timestamp']-startdate)/60
                torque = sensorValue['sensorData']['torque']
                power = sensorValue['sensorData']['power']
                cadence = sensorValue['sensorData']['cadence']

                csvstr += str(minutes)+','+str(torque)+",,"+str(power)+",,"+str(cadence)+",,\n"
    
    with open(output_path, 'w+') as ofile:
        ofile.write(csvstr)

if __name__ == '__main__':
    json_to_csv(sys.argv[1], sys.argv[2])
