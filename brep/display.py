"""
Routines for viewing Brep solids etc.
"""

import vtk


def show_solid(solid):
    points, cells = solid.as_polydata()
    
    pd = vtk.vtkPolyData()
    
    ps = vtk.vtkPoints()
    for i,p in enumerate(points):
        idx = ps.InsertNextPoint(p)
        assert idx==i
    pd.SetPoints(ps)
        
    ca = vtk.vtkCellArray()
    for c in cells:
        ca.InsertNextCell(len(c))
        for id in c:
            ca.InsertCellPoint(id)
            print id,
        print
            
    pd.SetPolys(ca)
    
    tri = vtk.vtkTriangleFilter()
    tri.SetInput(pd)
    
    map = vtk.vtkPolyDataMapper()
    map.SetInput(tri.GetOutput())
    
    act = vtk.vtkActor()
    act.SetMapper(map)
    
    ren = vtk.vtkRenderer()
    ren.AddActor(act)
    ren.SetBackground(0.5,0.5,0.5)

    ids = vtk.vtkIdFilter()
    ids.SetInput(pd)
    ids.PointIdsOn()

    visPts = vtk.vtkSelectVisiblePoints()
    visPts.SetInputConnection(ids.GetOutputPort())
    visPts.SetRenderer(ren)

    ldm = vtk.vtkLabeledDataMapper()
    ldm.SetLabelModeToLabelIds()
    #ldm.SetLabelModeToLabelFieldData()
    ldm.SetInputConnection(visPts.GetOutputPort())

    pointLabels = vtk.vtkActor2D()
    pointLabels.SetMapper(ldm)
    
    ren.AddActor2D(pointLabels)
    
    renwin = vtk.vtkRenderWindow()
    renwin.AddRenderer(ren)
    
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renwin)
    iren.Initialize()
    iren.Start()
        
    