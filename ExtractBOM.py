#Author-Autodesk Inc.
#Description-Extract BOM information from active design.

import adsk.core, adsk.fusion, traceback

def spacePadRight(value, length):
    pad = ''
    if type(value) is str:
        paddingLength = length - len(value) + 1
    else:
        paddingLength = length - value + 1
    while paddingLength > 0:
        pad += ' '
        paddingLength -= 1

    return str(value) + pad

def walkThrough(bom):
    mStr = ''
    for item in bom:
        mStr += spacePadRight(item['name'], 25) + str(spacePadRight(item['instances'], 15)) + str(item['volume']) + ' ' + str(item['bodies']) + ' '
        cog = item['cog']
        if cog:
            mStr += str(item['cog'].x)+ ' ' + str(item['cog'].y)+ ' ' + str(item['cog'].z)
        else:
            mStr += '? ? ?'
        mStr += '\n'
    return mStr

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
                volume = 0
                cog = None
                bodies = comp.bRepBodies
                body_count = 0
                for bodyK in bodies:
                    if bodyK.isSolid:
                        volume += bodyK.volume
                        cog = bodyK.physicalProperties.centerOfMass
                        body_count = body_count + 1
                
                # Add this component to the BOM
                bom.append({
                    'component': comp,
                    'name': comp.name,
                    'instances': 1,
                    'volume': volume,
                    'cog': cog,
                    'bodies' : body_count
                })

        # Display the BOM
        title = spacePadRight('Name', 25) + spacePadRight('Instances', 15) + 'Volume' + spacePadRight('', 25) + spacePadRight('', 15) + 'Bodies  CoG \n'
        msg = title + '\n' + walkThrough(bom)
        
        ui.messageBox(msg, 'Bill Of Materials')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
