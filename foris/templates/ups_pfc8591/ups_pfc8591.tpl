
%rebase("config/base.tpl", **locals())

<div id="page-ups-pfc8591" class="config-page">
%include("_messages.tpl")
  <div id="canvas-container">
%for fld in ["voltage", "light", "temperature", "trimmer"]:
    <canvas id="canvas-{{ fld }}"></canvas>
%end
  </div>
</div>


<script>
var graph_data = {
%for fld in ["voltage", "light", "temperature", "trimmer"]:
  "{{ fld }}": [
%	for _, val in enumerate(data[fld]):
    {{ val[1] }},
%	end
  ],
%end
};
var graph_labels = {
%for fld in ["voltage", "light", "temperature", "trimmer"]:
  "{{ fld }}": [
%	for _, val in enumerate(data[fld]):
    "{{ val[0] }}",
%	end
  ],
%end
};
</script>
