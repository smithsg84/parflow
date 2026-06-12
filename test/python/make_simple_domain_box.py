import vtk
from pathlib import Path

from collections import defaultdict

from pathlib import Path
from collections import defaultdict

from pathlib import Path
from collections import defaultdict

from pathlib import Path
from collections import defaultdict

def vtk_to_pfsol(vtk_path, pfsol_path=None, version=1):
    vtk_path = Path(vtk_path)
    pfsol_path = Path(pfsol_path) if pfsol_path else vtk_path.with_suffix(".pfsol")

    lines = vtk_path.read_text().splitlines()

    points = []
    triangles = []
    polygon_to_triangles = []
    cell_data = {}

    i = 0
    while i < len(lines):
        parts = lines[i].strip().split()
        if not parts:
            i += 1
            continue

        key = parts[0].upper()

        if key == "POINTS":
            n_points = int(parts[1])
            i += 1

            values = []
            while len(values) < 3 * n_points:
                values.extend(lines[i].strip().split())
                i += 1

            coords = list(map(float, values))
            points = [
                (coords[j], coords[j + 1], coords[j + 2])
                for j in range(0, 3 * n_points, 3)
            ]
            continue

        if key == "POLYGONS":
            n_polys = int(parts[1])
            i += 1

            for _ in range(n_polys):
                vals = list(map(int, lines[i].strip().split()))
                i += 1

                n = vals[0]
                verts = vals[1:]

                if n != len(verts):
                    raise ValueError(f"Malformed polygon line: {vals}")
                if n < 3:
                    raise ValueError(f"Polygon has fewer than 3 vertices: {vals}")

                start = len(triangles)

                # Fan triangulation:
                # v0 v1 v2 v3 -> (v0,v1,v2), (v0,v2,v3)
                for j in range(1, n - 1):
                    triangles.append((verts[0], verts[j], verts[j + 1]))

                polygon_to_triangles.append(list(range(start, len(triangles))))

            continue

        if key == "CELL_DATA":
            n_cells = int(parts[1])
            i += 1

            while i < len(lines):
                parts = lines[i].strip().split()
                if not parts:
                    i += 1
                    continue

                if parts[0].upper() != "SCALARS":
                    break

                name = parts[1]
                i += 1

                if i < len(lines):
                    maybe_lookup = lines[i].strip().split()
                    if maybe_lookup and maybe_lookup[0].upper() == "LOOKUP_TABLE":
                        i += 1

                values = []
                while len(values) < n_cells and i < len(lines):
                    next_parts = lines[i].strip().split()
                    if next_parts and next_parts[0].upper() in {
                        "SCALARS", "VECTORS", "FIELD", "POINT_DATA", "CELL_DATA"
                    }:
                        break
                    values.extend(next_parts)
                    i += 1

                cell_data[name] = list(map(int, values[:n_cells]))

            continue

        i += 1

    if not points:
        raise ValueError("No POINTS section found.")
    if not triangles:
        raise ValueError("No POLYGONS section found.")

    n_triangles = len(triangles)

    def expand_cell_data(name, default):
        original = cell_data.get(name)
        if original is None:
            return [default] * n_triangles

        if len(original) != len(polygon_to_triangles):
            raise ValueError(
                f"{name} CELL_DATA length does not match original polygon count."
            )

        expanded = [default] * n_triangles

        for poly_id, tri_ids in enumerate(polygon_to_triangles):
            print(f"poly_id={poly_id} trid_ids={tri_ids} original={original[poly_id]}")
            for tri_id in tri_ids:
                expanded[tri_id] = original[poly_id]

        return expanded

    solid_ids = expand_cell_data("solid_id", 0)

    print(cell_data)

    # If no patch_id exists, put every triangle in patch 0.
    patch_default = 0 if "patch_index" not in cell_data else -1

    print(patch_default)
    patch_ids = expand_cell_data("patch_index", patch_default)
    print(f"patch_ids = {patch_ids}")


    solids = defaultdict(list)
    for tri_id, tri in enumerate(triangles):
        for v in tri:
            if not 0 <= v < len(points):
                raise ValueError(f"Triangle {tri} references invalid vertex {v}")

        solids[solid_ids[tri_id]].append((tri, patch_ids[tri_id]))

    print(f"solids = {solids}")

    with pfsol_path.open("w", newline="\n") as f:
        f.write(f"{version}\n")

        f.write(f"{len(points)}\n")
        for x, y, z in points:
            f.write(f"{x:.17g} {y:.17g} {z:.17g}\n")

        f.write(f"{len(solids)}\n")

        for solid_id in sorted(solids):
            solid_tris = solids[solid_id]

            f.write(f"{len(solid_tris)}\n")
            for tri, _patch_id in solid_tris:
                f.write(f"{tri[0]} {tri[1]} {tri[2]}\n")

            patch_to_local_triangles = defaultdict(list)

            for local_tri_id, (_tri, patch_id) in enumerate(solid_tris):
                if patch_id >= 0:
                    patch_to_local_triangles[patch_id].append(local_tri_id)

            # Critical fix:
            # pfsol patches are identified by order, not by an explicit ID.
            # Therefore write empty patch blocks for missing patch IDs.
            if patch_to_local_triangles:
                num_patches = max(patch_to_local_triangles) + 1
            else:
                num_patches = 0

            f.write(f"{num_patches}\n")

            for patch_id in range(num_patches):
                local_ids = patch_to_local_triangles.get(patch_id, [])
                f.write(f"{len(local_ids)}\n")
                for local_tri_id in local_ids:
                    f.write(f"{local_tri_id}\n")

    return pfsol_path

def pfsol_to_vtk(pfsol_path, vtk_path=None):
    """
    Convert a ParFlow .pfsol solid file with 0-based indices
    to legacy ASCII VTK POLYDATA.
    """
    pfsol_path = Path(pfsol_path)
    vtk_path = Path(vtk_path) if vtk_path else pfsol_path.with_suffix(".vtk")

    tokens = pfsol_path.read_text().split()
    pos = 0

    def next_int():
        nonlocal pos
        value = int(tokens[pos])
        pos += 1
        return value

    def next_float():
        nonlocal pos
        value = float(tokens[pos])
        pos += 1
        return value

    version = next_int()

    n_vertices = next_int()
    vertices = [
        (next_float(), next_float(), next_float())
        for _ in range(n_vertices)
    ]

    n_solids = next_int()

    cells = []
    solid_ids = []
    local_triangle_ids = []
    patch_ids = []

    for solid_id in range(n_solids):
        n_triangles = next_int()

        local_triangles = [
            (next_int(), next_int(), next_int())
            for _ in range(n_triangles)
        ]

        local_patch_ids = [-1] * n_triangles

        n_patches = next_int()
        for patch_id in range(n_patches):
            n_patch_triangles = next_int()
            for _ in range(n_patch_triangles):
                tri_id = next_int()
                local_patch_ids[tri_id] = patch_id

        for tri_id, triangle in enumerate(local_triangles):
            cells.append(triangle)
            solid_ids.append(solid_id)
            local_triangle_ids.append(tri_id)
            patch_ids.append(local_patch_ids[tri_id])

    if pos != len(tokens):
        raise ValueError(
            f"Extra tokens after parsing {pfsol_path}: "
            f"{len(tokens) - pos} remaining"
        )

    with vtk_path.open("w", newline="\n") as f:
        f.write("# vtk DataFile Version 3.0\n")
        f.write(f"Converted from {pfsol_path.name}; pfsol version {version}\n")
        f.write("ASCII\n")
        f.write("DATASET POLYDATA\n")

        f.write(f"POINTS {len(vertices)} float\n")
        for x, y, z in vertices:
            f.write(f"{x:.17g} {y:.17g} {z:.17g}\n")

        f.write(f"POLYGONS {len(cells)} {len(cells) * 4}\n")
        for a, b, c in cells:
            if not (
                0 <= a < n_vertices
                and 0 <= b < n_vertices
                and 0 <= c < n_vertices
            ):
                raise ValueError(f"Triangle references invalid vertex: {(a, b, c)}")
            f.write(f"3 {a} {b} {c}\n")

        f.write(f"CELL_DATA {len(cells)}\n")

        f.write("SCALARS solid_id int 1\n")
        f.write("LOOKUP_TABLE default\n")
        for value in solid_ids:
            f.write(f"{value}\n")

        f.write("SCALARS local_triangle_id int 1\n")
        f.write("LOOKUP_TABLE default\n")
        for value in local_triangle_ids:
            f.write(f"{value}\n")

        f.write("SCALARS patch_id int 1\n")
        f.write("LOOKUP_TABLE default\n")
        for value in patch_ids:
            f.write(f"{value}\n")

    return vtk_path

vtk_path="box_100x100x5_rotated_45.vtk"

import vtk

# Create a 50x50x0.05 Box
cube = vtk.vtkCubeSource()
cube.SetBounds(-25.0, 25.0, -25.0, 25.0, -0.025, 0.025)
cube.Update()

# Rotate the cube 45 degrees about Z
transform = vtk.vtkTransform()
transform.RotateZ(45)

transform_filter = vtk.vtkTransformPolyDataFilter()
transform_filter.SetTransform(transform)
transform_filter.SetInputConnection(cube.GetOutputPort())
transform_filter.Update()

poly = transform_filter.GetOutput()

# Shift to positive coordinates
bounds = poly.GetBounds()
xmin, xmax, ymin, ymax, zmin, zmax = bounds

shift = vtk.vtkTransform()
shift.Translate(-xmin, -ymin, -zmin)

shift_filter = vtk.vtkTransformPolyDataFilter()
shift_filter.SetTransform(shift)
shift_filter.SetInputData(poly)
shift_filter.Update()

poly = shift_filter.GetOutput()

# Recompute bounds after shift
bounds = poly.GetBounds()
print(f"bounds = {bounds}")
zmin, zmax = bounds[4], bounds[5]
eps = 1e-6

patch_index = vtk.vtkIntArray()
patch_index.SetName("patch_index")
patch_index.SetNumberOfComponents(1)
patch_index.SetNumberOfTuples(poly.GetNumberOfCells())

for i in range(poly.GetNumberOfCells()):
    cell = poly.GetCell(i)

    zsum = 0.0
    for j in range(cell.GetNumberOfPoints()):
        pid = cell.GetPointId(j)
        print(f"poly.GetPoint = {poly.GetPoint(pid)}")
        zsum += poly.GetPoint(pid)[2]

    print(f"zsum={zsum}")        
    zavg = zsum / cell.GetNumberOfPoints()

    print(f"zavg={zavg}")

    if abs(zavg - zmax) < eps:
        patch_index.SetValue(i, 0)  # +Z
    elif abs(zavg - zmin) < eps:
        patch_index.SetValue(i, 1)  # -Z
    else:
        patch_index.SetValue(i, 2)  # X and Y faces

poly.GetCellData().AddArray(patch_index)
poly.GetCellData().SetScalars(patch_index)

writer = vtk.vtkPolyDataWriter()
writer.SetFileName(vtk_path)
writer.SetInputData(poly)
writer.SetFileTypeToASCII()
writer.Write()

print(f"Wrote {vtk_path}")

vtk_to_pfsol(vtk_path)

vtk_path = Path(vtk_path)
pfsol_to_vtk(vtk_path.with_suffix(".pfsol"), "back.vtk")
