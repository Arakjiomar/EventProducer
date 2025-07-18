import gzip

def parse_lhe_file(file_path):
    events = []
    current_event = None
    
    with gzip.open(file_path, 'rt') as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            
            if line.startswith('<event>'):
                current_event = {'particles': []}
            elif line.startswith('</event>'):
                if current_event:
                    # Only add the event if it contains particles
                    if current_event['particles']:
                        events.append(current_event)
                    current_event = None
            elif current_event is not None:
                # Skip comments and empty lines
                if not line.startswith('#') and line:
                    parts = line.split()
                    if len(parts) == 12:
                        pdg_id = int(parts[0])
                        status = int(parts[1])
                        mother1 = int(parts[2])
                        mother2 = int(parts[3])
                        color1 = int(parts[4])
                        color2 = int(parts[5])
                        px = float(parts[6])
                        py = float(parts[7])
                        pz = float(parts[8])
                        e = float(parts[9])
                        mass = float(parts[10])
                        lifetime = float(parts[11])
                        
                        particle = {
                            'pdg_id': pdg_id,
                            'status': status,
                            'mother1': mother1,
                            'mother2': mother2,
                            'color1': color1,
                            'color2': color2,
                            'momentum': (px, py, pz),
                            'energy': e,
                            'mass': mass,
                            'lifetime': lifetime
                        }
                        current_event['particles'].append(particle)
                    else:
                        # Skip lines that do not match the expected format
                        continue
    
    return events

def save_events_to_txt(events, output_file):
    with open(output_file, 'w') as f:
        for i, event in enumerate(events):
            f.write(f"Event {i+1}:\n")
            for particle in event['particles']:
                f.write(f"  PDG ID: {particle['pdg_id']}, Status: {particle['status']}, Momentum: {particle['momentum']}, Mass: {particle['mass']}\n")
            f.write("\n")

# Path to your compressed LHE file
file_path = '/eos/home-o/oarakji/tth/lhe/mg_pp_vbf_h01j_5f_50TeV/events_198624023.lhe.gz'

# Output file path
output_file = 'events_data.txt'

# Parse the LHE file
events = parse_lhe_file(file_path)

# Save important data to a text file
save_events_to_txt(events, output_file)

print(f"Data has been saved to {output_file}")