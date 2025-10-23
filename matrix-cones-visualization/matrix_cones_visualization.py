import numpy as np
import plotly.graph_objects as go


def compute_determinant(a, b, c):
    return a * c - b**2


def create_cone_boundary(a_range, c_range, num_points=80):
    a = np.linspace(a_range[0], a_range[1], num_points)
    c = np.linspace(c_range[0], c_range[1], num_points)
    A, C = np.meshgrid(a, c)
    B_pos = np.sqrt(np.maximum(A * C, 0))
    B_neg = -np.sqrt(np.maximum(A * C, 0))
    return A, B_pos, B_neg, C


def sample_cone_with_determinant(n_samples=1000, cone_type='pd'):
    points = []
    dets = []

    if cone_type == 'pd':
        for _ in range(n_samples):
            a = np.random.uniform(0.05, 5)
            c = np.random.uniform(0.05, 5)
            max_b = np.sqrt(a * c)
            ratio = np.random.beta(2, 2)
            b = np.random.uniform(-max_b * ratio, max_b * ratio)
            det = compute_determinant(a, b, c)
            points.append([a, b, c])
            dets.append(det)

    elif cone_type == 'nd':
        for _ in range(n_samples):
            a = np.random.uniform(-5, -0.05)
            c = np.random.uniform(-5, -0.05)
            max_b = np.sqrt(a * c)
            ratio = np.random.beta(2, 2)
            b = np.random.uniform(-max_b * ratio, max_b * ratio)
            det = compute_determinant(a, b, c)
            points.append([a, b, c])
            dets.append(det)

    elif cone_type == 'indefinite':
        for _ in range(n_samples):
            a = np.random.uniform(-5, 5)
            c = np.random.uniform(-5, 5)
            min_b = np.sqrt(np.abs(a * c)) * 1.05
            max_b = min_b + 4
            b = np.random.choice([-1, 1]) * np.random.uniform(min_b, max_b)
            det = compute_determinant(a, b, c)
            points.append([a, b, c])
            dets.append(det)

    return np.array(points), np.array(dets)


def create_visualization():
    fig = go.Figure()

    A_pos, B_pos, B_neg, C_pos = create_cone_boundary([0.01, 5], [0.01, 5], num_points=100)

    fig.add_trace(go.Surface(
        x=A_pos, y=B_pos, z=C_pos,
        name='PD Boundary (det=0, Barrier→∞)',
        colorscale=[[0, 'black'], [1, 'black']],
        opacity=0.8,
        showscale=False,
        hovertemplate='<b>PD BOUNDARY</b><br>a: %{x:.2f}<br>b: %{y:.2f}<br>c: %{z:.2f}<br>det = 0<br><b>Barrier → ∞</b><extra></extra>',
        lighting=dict(ambient=0.9, diffuse=0.7, specular=0.5)
    ))

    fig.add_trace(go.Surface(
        x=A_pos, y=B_neg, z=C_pos,
        name='PD Boundary (det=0)',
        colorscale=[[0, 'black'], [1, 'black']],
        opacity=0.8,
        showscale=False,
        showlegend=False,
        hovertemplate='<b>PD BOUNDARY</b><br>a: %{x:.2f}<br>b: %{y:.2f}<br>c: %{z:.2f}<br>det = 0<br><b>Barrier → ∞</b><extra></extra>',
        lighting=dict(ambient=0.9, diffuse=0.7, specular=0.5)
    ))

    A_neg, B_pos_neg, B_neg_neg, C_neg = create_cone_boundary([-5, -0.01], [-5, -0.01], num_points=100)

    fig.add_trace(go.Surface(
        x=A_neg, y=B_pos_neg, z=C_neg,
        name='ND Boundary (det=0, no barrier)',
        colorscale=[[0, 'darkred'], [1, 'red']],
        opacity=0.4,
        showscale=False,
        hovertemplate='<b>ND BOUNDARY</b><br>a: %{x:.2f}<br>b: %{y:.2f}<br>c: %{z:.2f}<br>det = 0<br>(barrier function not used for ND)<extra></extra>'
    ))

    fig.add_trace(go.Surface(
        x=A_neg, y=B_neg_neg, z=C_neg,
        name='ND Boundary',
        colorscale=[[0, 'darkred'], [1, 'red']],
        opacity=0.4,
        showscale=False,
        showlegend=False,
        hovertemplate='<b>ND BOUNDARY</b><br>a: %{x:.2f}<br>b: %{y:.2f}<br>c: %{z:.2f}<br>det = 0<br>(barrier function not used for ND)<extra></extra>'
    ))

    pd_points, pd_dets = sample_cone_with_determinant(800, 'pd')
    nd_points, nd_dets = sample_cone_with_determinant(400, 'nd')
    indef_points, indef_dets = sample_cone_with_determinant(300, 'indefinite')

    fig.add_trace(go.Scatter3d(
        x=pd_points[:, 0],
        y=pd_points[:, 1],
        z=pd_points[:, 2],
        mode='markers',
        name='PD Interior (det > 0)',
        marker=dict(
            size=3,
            color=pd_dets,
            colorscale='Greens',
            cmin=0,
            cmax=np.percentile(pd_dets, 90),
            colorbar=dict(title='det(X)', x=1.02, len=0.4, y=0.75),
            opacity=0.7,
            line=dict(width=0)
        ),
        hovertemplate='a: %{x:.2f}<br>b: %{y:.2f}<br>c: %{z:.2f}<br>det: %{marker.color:.3f}<extra>PD</extra>'
    ))

    fig.add_trace(go.Scatter3d(
        x=nd_points[:, 0],
        y=nd_points[:, 1],
        z=nd_points[:, 2],
        mode='markers',
        name='ND Interior (det > 0)',
        marker=dict(
            size=2.5,
            color=nd_dets,
            colorscale='Reds',
            cmin=0,
            cmax=np.percentile(nd_dets, 90),
            opacity=0.6,
            line=dict(width=0)
        ),
        hovertemplate='a: %{x:.2f}<br>b: %{y:.2f}<br>c: %{z:.2f}<br>det: %{marker.color:.3f}<extra>ND</extra>'
    ))

    fig.add_trace(go.Scatter3d(
        x=indef_points[:, 0],
        y=indef_points[:, 1],
        z=indef_points[:, 2],
        mode='markers',
        name='Indefinite (det < 0)',
        marker=dict(
            size=2,
            color=-indef_dets,
            colorscale='Blues',
            cmin=0,
            cmax=np.percentile(-indef_dets, 80),
            colorbar=dict(title='-det(X)', x=1.02, len=0.4, y=0.25),
            opacity=0.4,
            line=dict(width=0)
        ),
        hovertemplate='a: %{x:.2f}<br>b: %{y:.2f}<br>c: %{z:.2f}<br>det: %{customdata:.3f}<extra>Indefinite</extra>',
        customdata=indef_dets
    ))

    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        name='Origin (det=0)',
        marker=dict(size=10, color='black', symbol='diamond', line=dict(color='white', width=2)),
        hovertemplate='<b>Origin</b><br>(0, 0, 0)<br>det = 0<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': 'Positive Definite Cone with Barrier Function: B(X) = -log(det(X))<br><sub>Black surface = PD boundary where det(X) = 0 and Barrier → ∞ | Red surface = ND boundary (no barrier)</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=15)
        },
        scene=dict(
            xaxis_title='a = X₁₁',
            yaxis_title='b = X₁₂ = X₂₁',
            zaxis_title='c = X₂₂',
            camera=dict(eye=dict(x=1.4, y=1.4, z=1.2)),
            aspectmode='cube',
            xaxis=dict(gridcolor='lightgray', backgroundcolor='white'),
            yaxis=dict(gridcolor='lightgray', backgroundcolor='white'),
            zaxis=dict(gridcolor='lightgray', backgroundcolor='white')
        ),
        width=1400,
        height=1000,
        showlegend=True,
        legend=dict(
            x=0.01,
            y=0.99,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='black',
            borderwidth=1
        ),
        annotations=[
            dict(
                text=(
                    '<b>Barrier Function B(X) = -log(det(X)) for PD Matrices:</b><br><br>'
                    '🟢 <b>PD cone interior (green points):</b><br>'
                    '   det(X) > 0 → barrier is finite<br>'
                    '   Darker green = closer to boundary (smaller det)<br><br>'
                    '⬛ <b>PD boundary (BLACK surface):</b><br>'
                    '   det(X) = 0 → Barrier → ∞<br>'
                    '   This is where barrier prevents leaving PD cone<br><br>'
                    '🔴 <b>ND cone (red):</b> det > 0 but a,c < 0<br>'
                    '   Barrier function NOT used here<br><br>'
                    '🔵 <b>Indefinite region (blue):</b> det < 0<br>'
                    '   Outside both cones'
                ),
                showarrow=False,
                xref='paper',
                yref='paper',
                x=0.01,
                y=0.01,
                xanchor='left',
                yanchor='bottom',
                bgcolor='rgba(255, 255, 255, 0.95)',
                bordercolor='black',
                borderwidth=2,
                font=dict(size=10)
            )
        ]
    )
    return fig


if __name__ == '__main__':
    fig = create_visualization()
    fig.write_html('matrix_cones_visualization.html')