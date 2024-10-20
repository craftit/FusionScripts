#Author-Autodesk Inc.
#Description-Extract BOM information from active design.

import adsk.core, adsk.fusion, traceback
import io


def walkThrough(bom, filename):
    # Open a file for writing
    with io.open(filename, 'w', encoding='utf-8') as file:
        # Write the header
        file.write('Name,Body,Part Number,Volume,CoG X, CoG Y,Cog Z\n')
        for item in bom:
            mStr = item['name'] + ',' + item['body_name'] + ',' + item['part'] + ',' +  str(item['volume']) + ','
            cog = item['cog']
            if cog:
                mStr += str(item['cog'].x)+ ',' + str(item['cog'].y)+ ',' + str(item['cog'].z)
            else:
                mStr += '?,?,?'
            mStr += '\n'
            file.write(mStr)

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        title = 'Extract BOM'
        if not design:
            ui.messageBox('The DESIGN workspace must be active when running this script.', title)
            return

        # Get all occurrences in the root component of the active design
        root = design.rootComponent
        occs = root.allOccurrences
        
        # Gather information about each unique component
        bom = []
        for occ in occs:
            comp = occ.component
            
            jj = 0
            for bomI in bom:
                if bomI['component'] == comp:
                    # Increment the instance count of the existing row.
                    bomI['instances'] += 1
                    break
                jj += 1

            if jj == len(bom):
                # Gather any BOM worthy values from the component
                bodies = comp.bRepBodies
                bom.append({
                    'component': comp,
                    'part': comp.partNumber,
                    'body_name': bodies[0].name if bodies else 'No Body',
                    'name': comp.name,
                    'volume': comp.physicalProperties.volume,
                    'instances': 1,

                    'cog': comp.physicalProperties.centerOfMass
                })
                # comp.physicalProperties
                # for bodyK in bodies:
                #     if bodyK.isSolid:
                #         bom.append({
                #             'component': comp,
                #             'name': comp.name,
                #             'body_name': bodyK.name,
                #             'volume': bodyK.volume,
                #             'cog': bodyK.physicalProperties.centerOfMass
                #         })
                

        # Display the BOM
        filename = "extractedBOM.csv"
        fileDlg = ui.createFileDialog()
        fileDlg.isMultiSelectEnabled = False
        fileDlg.title = 'Save BOM to file'
        fileDlg.filter = 'CSV files (*.csv)'
        dlgResult = fileDlg.showSave()
        if dlgResult == adsk.core.DialogResults.DialogOK:
            filename = fileDlg.filename            
            walkThrough(bom, filename=filename)
            ui.messageBox(f"Bom save to: {filename}", "File saved ok")
        else:
            ui.messageBox('No file was selected.', "Save aborted")

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
