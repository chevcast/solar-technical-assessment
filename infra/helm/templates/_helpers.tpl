{{- define "solar.labels" -}}
app.kubernetes.io/name:  {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "solar.fullname" -}}
{{ printf "%s-%s" .Release.Name .Chart.Name }}
{{- end }}
