class_name GenericInfoDisplay
extends Node

@export var title: String
@export_multiline var description: String 

@export var title_label: RichTextLabel
@export var description_label: RichTextLabel

# Called when the node enters the scene tree for the first time.
func _ready():
	if title:
		set_title(title)
	if description:
		set_description(description)

func set_visible(visible: bool):
	self.visible = visible

func set_data(title: String, description: String):
	set_title(title)
	set_description(description)

func set_title(title: String):
	self.title_label.text = title
	
func set_description(description: String):
	self.description_label.text = description
