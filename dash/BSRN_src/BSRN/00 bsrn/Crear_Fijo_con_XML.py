import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET

def abrir_archivo():
    # Abrir el cuadro de diálogo para seleccionar un archivo
    ruta_archivo = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
    respuesta = messagebox.askyesno("Agregar Leyenda", "¿Desea agregar nota de error en UV?")
    
    if ruta_archivo:
        # Procesar el archivo seleccionado
        resultado = procesar_archivo_xml(ruta_archivo,respuesta)
        if resultado:
            messagebox.showinfo("Éxito", "El archivo se procesó correctamente.")
        else:
            messagebox.showerror("Error", "Hubo un problema al procesar el archivo.")

# Función para procesar el archivo XML
def procesar_archivo_xml(ruta_archivo,agregar_leyenda):
    try:
        # Tu código para leer el archivo XML y obtener el root
        tree = ET.parse(ruta_archivo)
        root = tree.getroot()
        
        # Extraer datos C0001
        station_id = root.find(".//FirstData").get("stationId")
        month_measurement = root.find(".//FirstData").get("monthMeasurement")
        year_measurement = root.find(".//FirstData").get("yearMeasurement")
        version_data = root.find(".//FirstData").get("versionData")

        values = [int(qm.get("value")) for qm in root.findall(".//FirstData/quantityMeasured")]

        # Extraer datos U0002
        scientist_changed_day = root.find(".//SecondData").get("scientistChangedDay")
        scientist_changed_hour = root.find(".//SecondData").get("scientistChangedHour")
        scientist_changed_min = root.find(".//SecondData").get("scientistChangedMin")
        name_station_scientist = root.find(".//SecondData").get("nameStationScientist")
        telephone_station_scientist = root.find(".//SecondData").get("telephoneStationScientist")
        fax_station_scientist = root.find(".//SecondData").get("faxStationScientist")
        tcp_ip_station_scientist = root.find(".//SecondData").get("tcpIpStationScientis")
        email_station_scientist = root.find(".//SecondData").get("emailStationScientis")
        address_station_scientist = root.find(".//SecondData").get("addresStationScientist")
        deputy_changed_day = root.find(".//SecondData").get("deputyChangedDay")
        deputy_changed_hour = root.find(".//SecondData").get("deputyChangedHour")
        deputy_changed_min = root.find(".//SecondData").get("deputyChangedMin")
        name_station_deputy = root.find(".//SecondData").get("nameStationDeputy")
        telephone_station_deputy = root.find(".//SecondData").get("telephoneStationDeputy")
        fax_station_deputy = root.find(".//SecondData").get("faxStationDeputy")
        tcp_ip_station_deputy = root.find(".//SecondData").get("tcpIpStationDeputy")
        email_station_deputy = root.find(".//SecondData").get("emailStationDeputy")
        address_station_deputy = root.find(".//SecondData").get("addresStationDeputy")


        # Extraer datos C0003
        lines = [line.get("value") for line in root.findall(".//ThirdData/Line")]

        # Extraer datos U0004
        station_description_changed_day = root.find(".//FourData").get("stationDescriptionChangedDay")
        station_description_changed_hour = root.find(".//FourData").get("stationDescriptionChangedHour")
        station_description_changed_min = root.find(".//FourData").get("stationDescriptionChangedMin")
        surface_type = root.find(".//FourData").get("surfaceType")
        topography_type = root.find(".//FourData").get("topographyType")
        address_station = root.find(".//FourData").get("addressStation")
        telephone_station = root.find(".//FourData").get("telephoneStation")
        fax_station = root.find(".//FourData").get("faxStation")
        tcp_ip_station = root.find(".//FourData").get("tcpIpStation")
        email_station = root.find(".//FourData").get("emailStation")
        latitude = root.find(".//FourData").get("latitude")
        longitude = root.find(".//FourData").get("longitude")
        altitude = root.find(".//FourData").get("altitude")
        identification_synop = root.find(".//FourData").get("identificationSYNOP")
        horizon_changed_day = root.find(".//FourData").get("horizonChangedDay")
        horizon_changed_hour = root.find(".//FourData").get("horizonChangedHour")
        horizon_changed_min = root.find(".//FourData").get("horizonChangedMin")

        # Extraer datos U0007
        changed_occurred_day = root.find(".//SevenData").get("changedOcurredDay")
        changed_occurred_hour = root.find(".//SevenData").get("changedOcurredHour")
        changed_occurred_min = root.find(".//SevenData").get("changedOcurredMin")
        method_est_cloud_amount = root.find(".//SevenData").get("methodEstCloundAmount")
        method_est_cloud_base_height = root.find(".//SevenData").get("methodEstCloundBaseHeight")
        method_est_cloud_liquid_water = root.find(".//SevenData").get("methodEstCloundLiquidWater")
        method_est_cloud_aerosol_vertical_dis = root.find(".//SevenData").get("methodEstCloundAerosolVerticalDis")
        method_est_water_vapour_press = root.find(".//SevenData").get("methodEstWaterVapourPress")

        flags = [flag.get("value") for flag in root.findall(".//flagsIndicatingIfTheSYNOP/flag")]
        flags = ['N' if flag == '0' else flag for flag in flags]




        # Rellenar los valores faltantes de C0001
        while len(values) < 16:
            values.append(-1)

        # Formatear la salida de C0001
        output = f"*C0001\n {station_id:>2}{month_measurement:>3}{year_measurement:>5}{version_data:>3}\n"
        output += " " * 1 + " ".join([f"{value:9}" for value in values[:8]]) + "\n"
        output += " " * 1 + " ".join([f"{value:9}" for value in values[8:]]) + "\n"

        # Formatear la salida de U0002
        output += "*U0002\n"
        output += f" {scientist_changed_day} {scientist_changed_hour} {scientist_changed_min}\n"
        output += f"{name_station_scientist:<40}{telephone_station_scientist:<20}{fax_station_scientist:<20}\n"
        output += f"{tcp_ip_station_scientist:<16}{email_station_scientist:<50}\n"
        output += f"{address_station_scientist:<80}\n"
        output += f" {deputy_changed_day} {deputy_changed_hour} {deputy_changed_min}\n"
        output += f"{name_station_deputy:<40}{telephone_station_deputy:<20}{fax_station_deputy:<20}\n"
        output += f"{tcp_ip_station_deputy:<16}{email_station_deputy:<50}\n"
        output += f"{address_station_deputy:<80}\n"

        # Formatear la salida de C0003
        output += "*C0003\n"
        if agregar_leyenda==True:
            output += "UV data was wrong and therefore deleted for this month\n"
        for line in lines:
            if len(line)<=80:
                output += f"{line}\n"
            else: 
                output += f"{line[:-2]}&\n" 
                output += f"{line[-2:]}\n" 

        # Formatear la salida de U0004
        output += "*U0004\n"
        output += f" {station_description_changed_day} {station_description_changed_hour} {station_description_changed_min}\n"
        output += f" {surface_type:3} {topography_type}\n"
        output += f"{address_station:<80}\n"
        output += f"{telephone_station:<21}{fax_station:<20}\n"
        output += f"{tcp_ip_station:<16}{email_station:<50}\n"
        output += f" {latitude:8} {longitude:7} {altitude:3} {identification_synop}\n"
        output += f" {horizon_changed_day} {horizon_changed_hour} {horizon_changed_min}\n"


        grades = root.findall(".//Grade")

        count = 0
        for grade in grades:
            azimuth = int(round(float(grade.get("azimuthDegress"))))
            elevation = int(round(float(grade.get("elevationDegress"))))
            output += f"{azimuth:>4}{elevation: >3}"
            count += 1
            if count % 11 == 0:  # Agrega un salto de línea cada 10 pares
                output += "\n"
            if azimuth == 359:
                output += f"{-1:>4}{-1: >3}"*8


        # Formatear la salida de U0007
        output += "\n*U0007\n"
        output += f" {changed_occurred_day} {changed_occurred_hour} {changed_occurred_min}\n"
        output += f"{method_est_cloud_amount:<80}\n"
        output += f"{method_est_cloud_base_height:<80}\n"
        output += f"{method_est_cloud_liquid_water:<80}\n"
        output += f"{method_est_cloud_aerosol_vertical_dis:<80}\n"
        output += f"{method_est_water_vapour_press:<80}\n"
        output += " ".join(flags) + "\n"


        # Extraer datos U0008
        output += "*U0008\n"
        for instrument_data in root.findall(".//EightData/instrument"):

            changed_occurred_day = instrument_data.get("changedOcurredDay")
            changed_occurred_hour = instrument_data.get("changedOcurredHour")
            changed_occurred_min = instrument_data.get("changedOcurredMin")
            is_instrument_measuring = instrument_data.get("isInstrumenMeasuring")
            is_instrument_measuring = "Y" if instrument_data.get("isInstrumenMeasuring") == "1" else instrument_data.get("isInstrumenMeasuring")


            manufacturer = instrument_data.get("manufacturer")
            model = instrument_data.get("model")
            serial_number = instrument_data.get("serialNumber")
            date_of_purchase = instrument_data.get("dateOfPurchase")
            identification_number = instrument_data.get("identificactionNumber")

            remarks_about_radiation = instrument_data.get("remarksAboutTheRadiation")
            remarks_calibration_units = instrument_data.get("remarksOnCalibrationEgUnitsOfCal")
            remarks_calibration_cont = instrument_data.get("remarksOnCalibrationContinued")

            pyrgeometer_body_code = instrument_data.get("pyrgeometerBodyCompensationCode")
            pyrgeometer_dome_code = instrument_data.get("pyrgeometerDomeCompensationCode")

            wavelength_band1 = instrument_data.get("wavelengthOfBand1")
            bandwidth_band1 = instrument_data.get("bandWidthOfBand1")
            bandwidth_band1 = "{:.3f}".format(float(instrument_data.get("bandWidthOfBand1")))
            wavelength_band2 = instrument_data.get("wavelengthOfBand2")
            bandwidth_band2 = instrument_data.get("bandWidthOfBand2")
            wavelength_band3 = instrument_data.get("wavelengthOfBand3")
            bandwidth_band3 = instrument_data.get("bandWidthOfBand3")

            max_zenith_angle = instrument_data.get("maxZenithAngle")
            min_spectral_instrument = instrument_data.get("minSpectralInstrument")

            location_of_calibration = instrument_data.get("locationOfCalibration")
            person_doing_calibration = instrument_data.get("personDoingCalibration")

            start_cal_period_band1 = instrument_data.get("startOfCalibrationPeriodBand1")
            end_cal_band1 = instrument_data.get("endOfCalibrationBand1")
            num_comparisons_band1 = instrument_data.get("numberOfComparisonsBand1")
            mean_cal_coef_band1 = instrument_data.get("meanCalibrationCoeficientBand1")
            mean_cal_coef_band1 = "{:.4f}".format(float(instrument_data.get("meanCalibrationCoeficientBand1")))
            std_error_cal_coef_band1 = instrument_data.get("standardErrorOfCalCoeffBanda1")
            std_error_cal_coef_band1 = "{:.4f}".format(float(instrument_data.get("standardErrorOfCalCoeffBanda1")))

            start_cal_period_band2 = instrument_data.get("startOfCalibrationPeriodBand2")
            end_cal_band2 = instrument_data.get("endOfCalibrationBand2")
            num_comparisons_band2 = instrument_data.get("numberOfComparisonsBand2")
            mean_cal_coef_band2 = instrument_data.get("meanCalibrationCoeficientBand2")
            mean_cal_coef_band2 = "{:.4f}".format(float(instrument_data.get("meanCalibrationCoeficientBand2")))
            std_error_cal_coef_band2 = instrument_data.get("standardErrorOfCalCoeffBanda2")
            std_error_cal_coef_band2 = "{:.4f}".format(float(instrument_data.get("standardErrorOfCalCoeffBanda2")))

            start_cal_period_band3 = instrument_data.get("startOfCalibrationPeriodBand3")
            end_cal_band3 = instrument_data.get("endOfCalibrationBand3")
            num_comparisons_band3 = instrument_data.get("numberOfComparisonsBand3")
            mean_cal_coef_band3 = instrument_data.get("meanCalibrationCoeficientBand3")
            mean_cal_coef_band3 = "{:.4f}".format(float(instrument_data.get("meanCalibrationCoeficientBand3")))
            std_error_cal_coef_band3 = instrument_data.get("standardErrorOfCalCoeffBanda3")
            std_error_cal_coef_band3 = "{:.4f}".format(float(instrument_data.get("standardErrorOfCalCoeffBanda3")))

            # Formatear la salida de U0008
            output += f" {changed_occurred_day} {changed_occurred_hour} {changed_occurred_min} {is_instrument_measuring}\n"
            output += f"{manufacturer:<31}{model:<16}{serial_number:<19}{date_of_purchase:<9}{identification_number}\n"
            output += f"{remarks_about_radiation:<80}\n"
            output += f" {pyrgeometer_body_code:>2}{pyrgeometer_dome_code:>3}{wavelength_band1:>8}{bandwidth_band1:>8}{wavelength_band2:>8}{bandwidth_band2:>8}{wavelength_band3:>8}{bandwidth_band3:>8}{max_zenith_angle:>3}{min_spectral_instrument:>3}\n"
            output += f"{location_of_calibration:<31}{person_doing_calibration:<40}\n"
            output += f"{start_cal_period_band1:<9}{end_cal_band1:<9}{num_comparisons_band1:<3}{mean_cal_coef_band1: >12}{std_error_cal_coef_band1:>13}\n"
            output += f"{start_cal_period_band2:<9}{end_cal_band2:<9}{num_comparisons_band2:<3}{mean_cal_coef_band2: >12}{std_error_cal_coef_band2:>13}\n"
            output += f"{start_cal_period_band3:<9}{end_cal_band3:<9}{num_comparisons_band3:<3}{mean_cal_coef_band3: >12}{std_error_cal_coef_band3:>13}\n"
            output += f"{remarks_calibration_units:<80}\n"
            output += f"{remarks_calibration_cont:<80}\n"

        # Formatear la salida de cada instrumento dentro de <NineData>
        output += "*U0009\n"
        for instrument in root.findall(".//NineData/instrument"):
            # Extraer los datos de cada instrumento
            changedOcurredDay = instrument.get("changedOcurredDay")
            changedOcurredHour = instrument.get("changedOcurredHour")
            changedOcurredMin = instrument.get("changedOcurredMin")
            id_quality_measured = instrument.get("idNoOfRadiationQualityMeasured")
            id_instrument_measured = instrument.get("idNoOfInstrumentWhichMeasuedQuality")
            no_of_band = instrument.get("noOfBandForSpectralInstruments")

            # Formatear los datos de cada instrumento
            formatted_data = f"{changedOcurredDay:>3}{changedOcurredHour:>3}{changedOcurredMin:>3}{id_quality_measured:>10} {id_instrument_measured:>5}{no_of_band:>3}\n"

            output += formatted_data

        output = output.rstrip('\n')

        with open('fijo.dat', 'w') as file:
            file.write(output)
        
        return True  # Devolver verdadero si el procesamiento se completó correctamente
        
    except Exception as e:
        print(e)  # Imprimir cualquier excepción que ocurra para depuración
        return False  # Devolver falso si hubo un error durante el procesamiento

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Seleccionar archivo XML")

# Botón para abrir el archivo
btn_abrir = tk.Button(root, text="Seleccionar Archivo XML", command=abrir_archivo)
btn_abrir.pack(padx=20, pady=20)

# Función para cerrar la ventana después de procesar el archivo
def cerrar_ventana():
    root.destroy()

# Llamar a la función de cierre después de procesar el archivo
btn_abrir.config(command=lambda: [abrir_archivo(), cerrar_ventana()])

# Iniciar la interfaz
root.mainloop()