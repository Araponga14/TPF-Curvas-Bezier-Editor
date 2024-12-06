import tkinter as tk
from tkinter import Frame, Label, Button, Entry, Checkbutton, IntVar, StringVar, Text, END
from tkinter import messagebox

class BezierEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor Interativo de Curvas de Bézier")

        # Configurações iniciais
        self.points = []              # Lista de pontos de controle [(x, y), ...]
        self.selected_point = None    # Índice do ponto selecionado
        self.dragging = False         # Flag para indicar se está arrastando um ponto
        self.show_control_polygon = True

        self.num_segments = 50        # Número de segmentos para desenhar a curva
        self.radius = 5               # Raio para desenhar os pontos de controle

        # Frame principal
        self.main_frame = Frame(root)
        self.main_frame.pack(side="top", fill="both", expand=True)

        # Canvas para desenho
        self.canvas_width = 800
        self.canvas_height = 600
        self.canvas = tk.Canvas(self.main_frame, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Painel lateral de controle
        self.side_frame = Frame(self.main_frame)
        self.side_frame.pack(side="right", fill="y")

        # Exibição de coordenadas (editáveis)
        self.coord_label = Label(self.side_frame, text="Coordenadas dos pontos:", font=("Arial", 10, "bold"))
        self.coord_label.pack(pady=5)

        self.coord_text = Text(self.side_frame, height=10, width=30)
        self.coord_text.pack()

        # Vincular evento Enter no campo de texto
        self.coord_text.bind("<Return>", self.on_coord_text_enter)

        # Label para mostrar o ponto selecionado
        self.selected_point_label = Label(self.side_frame, text="Ponto selecionado: Nenhum", font=("Arial", 10, "italic"))
        self.selected_point_label.pack(pady=5)

        # Controle de número de segmentos
        Label(self.side_frame, text="Número de segmentos:").pack(pady=5)
        self.seg_var = StringVar(value=str(self.num_segments))
        self.seg_entry = Entry(self.side_frame, textvariable=self.seg_var)
        self.seg_entry.pack(pady=5)

        # Botão para atualizar número de segmentos
        Button(self.side_frame, text="Atualizar Segmentos", command=self.update_segments).pack(pady=5)

        # Checkbutton para exibir/ocultar polígono de controle
        self.show_polygon_var = IntVar(value=1)
        self.show_polygon_check = Checkbutton(self.side_frame, text="Mostrar polígono de controle", variable=self.show_polygon_var, command=self.toggle_polygon)
        self.show_polygon_check.pack(pady=5)

        # Botão para remover ponto selecionado
        Button(self.side_frame, text="Remover Ponto Selecionado", command=self.remove_selected_point).pack(pady=5)
        
        # Botão para limpar todos os pontos
        Button(self.side_frame, text="Limpar Todos os Pontos", command=self.clear_all_points).pack(pady=5)

        # Instruções
        Label(self.side_frame, text="Instruções:", font=("Arial", 10, "bold")).pack(pady=10)
        instructions = (
            "Clique no canvas para adicionar um ponto.\n"
            "Clique em um ponto existente para selecioná-lo.\n"
            "Arraste um ponto selecionado para movê-lo.\n"
            "Edite as coordenadas no campo de texto e pressione Enter para atualizar.\n"
            "Pressione Backspace ou Delete para remover o ponto selecionado.\n"
            "Use 'Limpar Todos os Pontos' para começar de novo.\n"
            "Ajuste o número de segmentos para controlar a suavidade.\n"
            "Ative ou desative a exibição do polígono de controle."
        )
        Label(self.side_frame, text=instructions, wraplength=200, justify="left").pack(pady=5)

        # Eventos do mouse
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        # Eventos de teclado para remover ponto
        self.root.bind("<BackSpace>", self.on_delete_key)
        self.root.bind("<Delete>", self.on_delete_key)

        # Desenhar o estado inicial
        self.draw()

    def on_coord_text_enter(self, event):
        # Ao apertar Enter no campo de texto, tentar atualizar as posições dos pontos
        self.apply_edited_coordinates()
        return "break"  # Impede que o Enter seja adicionado no texto

    def on_delete_key(self, event):
        # Ao pressionar Backspace ou Delete, remover ponto selecionado
        self.remove_selected_point()

    def apply_edited_coordinates(self):
        # Ler todo o conteúdo do text e tentar parsear as coordenadas
        lines = self.coord_text.get("1.0", END).strip().split("\n")
        new_points = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                # Espera-se o formato: P{i}: (x, y)
                left, coords_str = line.split(":", 1)
                coords_str = coords_str.strip()
                coords_str = coords_str.strip("()")
                x_str, y_str = coords_str.split(",")
                x = float(x_str.strip())
                y = float(y_str.strip())
                new_points.append((x, y))
            except Exception:
                messagebox.showerror("Erro", f"Formato inválido na linha: {line}")
                return
        # Se chegou até aqui, podemos atualizar os pontos
        self.points = new_points
        # Atualizar seleção caso o índice selecionado não exista mais
        if self.selected_point is not None and (self.selected_point >= len(self.points)):
            self.selected_point = None
        self.draw()

    def toggle_polygon(self):
        self.show_control_polygon = bool(self.show_polygon_var.get())
        self.draw()

    def update_segments(self):
        try:
            val = int(self.seg_var.get())
            if val > 0:
                self.num_segments = val
                self.draw()
        except ValueError:
            pass

    def clear_all_points(self):
        self.points = []
        self.selected_point = None
        self.draw()

    def remove_selected_point(self):
        if self.selected_point is not None and 0 <= self.selected_point < len(self.points):
            del self.points[self.selected_point]
            self.selected_point = None
            self.draw()

    def on_canvas_click(self, event):
        # Verifica se clicou em um ponto existente
        clicked_index = self.get_clicked_point(event.x, event.y)
        if clicked_index is not None:
            # Seleciona o ponto clicado
            self.selected_point = clicked_index
        else:
            # Adiciona novo ponto na posição do clique
            self.points.append((event.x, event.y))
            self.selected_point = len(self.points) - 1
        self.draw()

    def on_canvas_drag(self, event):
        if self.selected_point is not None:
            # Arrasta ponto selecionado
            self.points[self.selected_point] = (event.x, event.y)
            self.draw()

    def on_canvas_release(self, event):
        # Ao soltar o mouse, finaliza o arrasto
        self.dragging = False

    def get_clicked_point(self, x, y):
        for i, (px, py) in enumerate(self.points):
            if (px - x)**2 + (py - y)**2 <= self.radius**2:
                return i
        return None

    def draw(self):
        self.canvas.delete("all")
        # Desenhar polígono de controle
        if self.show_control_polygon and len(self.points) > 1:
            for i in range(len(self.points)-1):
                self.canvas.create_line(self.points[i][0], self.points[i][1],
                                        self.points[i+1][0], self.points[i+1][1],
                                        fill="gray", dash=(4,2))

        # Desenhar pontos de controle
        for i, (x, y) in enumerate(self.points):
            fill_color = "red" if i == self.selected_point else "blue"
            self.canvas.create_oval(x-self.radius, y-self.radius, x+self.radius, y+self.radius, fill=fill_color, outline="black")

        # Desenhar curva de Bézier se houver 2 ou mais pontos
        if len(self.points) > 1:
            curve_points = self.compute_bezier_points(self.points, self.num_segments)
            # Desenhar a curva
            for i in range(len(curve_points)-1):
                self.canvas.create_line(curve_points[i][0], curve_points[i][1],
                                        curve_points[i+1][0], curve_points[i+1][1],
                                        fill="green", width=2)

        # Atualizar texto com coordenadas
        self.update_coord_text()

        # Atualizar Label do ponto selecionado
        self.update_selected_point_label()

    def update_coord_text(self):
        self.coord_text.delete("1.0", END)
        for i, (x, y) in enumerate(self.points):
            self.coord_text.insert(END, f"P{i}: ({x:.2f}, {y:.2f})\n")

    def update_selected_point_label(self):
        if self.selected_point is None:
            self.selected_point_label.config(text="Ponto selecionado: Nenhum")
        else:
            self.selected_point_label.config(text=f"Ponto selecionado: P{self.selected_point}")

    def compute_bezier_points(self, control_points, num_segments):
        result = []
        for i in range(num_segments+1):
            t = i / num_segments
            x, y = self.de_casteljau(control_points, t)
            result.append((x, y))
        return result

    def de_casteljau(self, points, t):
        if len(points) == 1:
            return points[0]
        new_points = []
        for i in range(len(points)-1):
            x1, y1 = points[i]
            x2, y2 = points[i+1]
            x = (1-t)*x1 + t*x2
            y = (1-t)*y1 + t*y2
            new_points.append((x, y))
        return self.de_casteljau(new_points, t)


if __name__ == "__main__":
    root = tk.Tk()
    app = BezierEditor(root)
    root.mainloop()
