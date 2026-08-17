from flask import Flask, render_template, request, Response
import math  # Used as per Lab Manual Module 1 (Section 1.1)
import ezdxf
from ezdxf import zoom
import io

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Detect which shape form was submitted
    shape_type = request.form.get('shape_type')
    
    # Initialize a clean R2010 AutoCAD template layout
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    doc.layers.new(name="OUTLINE", dxfattribs={"color": 7}) # Color 7 auto-toggles white/black screen
    
    # --- IF-ELIF-ELSE SELECTION STRUCTURE (Matching Lab Manual Section 1.1) ---
    if shape_type == "square":
        side = float(request.form.get('square_side', 50))
        # Map 4 corners of the square profile
        points = [(0, 0), (side, 0), (side, side), (0, side), (0, 0)]
        msp.add_lwpolyline(points, dxfattribs={"layer": "OUTLINE"})
        
    elif shape_type == "rectangle":
        length = float(request.form.get('rect_length', 80))
        width = float(request.form.get('rect_width', 40))
        # Map 4 corners of the rectangular profile
        points = [(0, 0), (length, 0), (length, width), (0, width), (0, 0)]
        msp.add_lwpolyline(points, dxfattribs={"layer": "OUTLINE"})
        
    elif shape_type == "circle":
        radius = float(request.form.get('circle_radius', 30))
        # Draw center point at origin (0,0) with calculated radius constraint
        msp.add_circle((0, 0), radius, dxfattribs={"layer": "OUTLINE"})
        
    elif shape_type == "triangle":
        tri_kind = request.form.get('tri_kind')
        
        if tri_kind == "right":
            base = float(request.form.get('right_base', 60))
            height = float(request.form.get('right_height', 40))
            points = [(0, 0), (base, 0), (0, height), (0, 0)]
            msp.add_lwpolyline(points, dxfattribs={"layer": "OUTLINE"})
            
        elif tri_kind == "obtuse":
            # Logic: Given Side A, Side B, and an obtuse angle (> 90 degrees)
            side_a = float(request.form.get('obtuse_a', 70))
            side_b = float(request.form.get('obtuse_b', 50))
            angle_deg = float(request.form.get('obtuse_angle', 120))
            
            # Apply standard math radian conversion explicitly covered in Lab Manual page 3
            angle_rad = math.radians(angle_deg)
            
            # Coordinate mapping using trigonometry functions (math.cos, math.sin)
            x3 = side_a + (side_b * math.cos(angle_rad))
            y3 = side_b * math.sin(angle_rad)
            
            points = [(0, 0), (side_a, 0), (x3, y3), (0, 0)]
            msp.add_lwpolyline(points, dxfattribs={"layer": "OUTLINE"})
            
        elif tri_kind == "acute":
            # Logic: Given a base side and two acute angles (< 90 degrees)
            base = float(request.form.get('acute_base', 80))
            angle_a_deg = float(request.form.get('acute_angle_a', 60))
            angle_b_deg = float(request.form.get('acute_angle_b', 50))
            
            rad_a = math.radians(angle_a_deg)
            rad_b = math.radians(angle_b_deg)
            
            # Solving top vertex coordinate point analytically using intercept math rules
            x3 = (base * math.tan(rad_b)) / (math.tan(rad_a) + math.tan(rad_b))
            y3 = x3 * math.tan(rad_a)
            
            points = [(0, 0), (base, 0), (x3, y3), (0, 0)]
            msp.add_lwpolyline(points, dxfattribs={"layer": "OUTLINE"})

    # Force view focal lens to automatically map bounding limits upon loading
    zoom.extents(msp)
    
    # Save into memory binary buffer for data stream delivery over HTTP
    stream = io.StringIO()
    doc.write(stream)
    dxf_output = stream.getvalue()
    
    return Response(
        dxf_output,
        mimetype="image/vnd.dxf",
        headers={"Content-Disposition": f"attachment; filename={shape_type}_shape.dxf"}
    )

if __name__ == '__main__':
    app.run(debug=True)
    