auth_token= 'eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDI3NzM1MDUsInR5cGUiOiJleHRlcm5hbCIsInVzZXIiOiJscmV5ZXNAdWRlc2EuZWR1LmFyIn0.psb9tQtUB0bPJgTwxnwH9gnXy1wLrBgF71ZE_dMLbQbz8FdeaHOUgqsIfpZgwJQioKapfEQhXVLCjsmzY1aA6w'

 # Get authorized token from BCRA web page
head = {'Authorization': 'Bearer ' + auth_token}

milestones = 'https://api.estadisticasbcra.com/milestones'
base = 'https://api.estadisticasbcra.com/base'
base_usd = 'https://api.estadisticasbcra.com/base_usd'
reserves = 'https://api.estadisticasbcra.com/reservas'
base_div_res = 'https://api.estadisticasbcra.com/base_div_res'
usd = 'https://api.estadisticasbcra.com/usd'
usd_official = 'https://api.estadisticasbcra.com/usd_of'
usd_of_minorista = 'https://api.estadisticasbcra.com/usd_of_minorista'
var_usd_vs_usd_official = 'https://api.estadisticasbcra.com/var_usd_vs_usd_of'
circulation = 'https://api.estadisticasbcra.com/circulacion_monetaria'
coins = 'https://api.estadisticasbcra.com/billetes_y_monedas'
cash_institutions = 'https://api.estadisticasbcra.com/efectivo_en_ent_fin'
deposits_institutions = 'https://api.estadisticasbcra.com/depositos_cuenta_ent_fin'
deposits = 'https://api.estadisticasbcra.com/depositos'
cuentas_corrientes = 'https://api.estadisticasbcra.com/cuentas_corrientes'
cajas_ahorro = 'https://api.estadisticasbcra.com/cajas_ahorro'
plazos_fijos = 'https://api.estadisticasbcra.com/plazo_fijo'
tasa_depositos30d = 'https://api.estadisticasbcra.com/tasa_depositos_30_dias'
prestamos = 'https://api.estadisticasbcra.com/prestamos'
tasa_prestamos_personales = 'https://api.estadisticasbcra.com/tasa_prestamos_personales'
tasa_adelantos_cuenta_corriente = 'https://api.estadisticasbcra.com/tasa_adelantos_cuenta_corriente'
porcentaje_prestamodeposito = 'https://api.estadisticasbcra.com/porc_prestamos_vs_depositos'
lebacs = 'https://api.estadisticasbcra.com/lebac'
leliqs = 'https://api.estadisticasbcra.com/leliq'
lebacs_usd = 'https://api.estadisticasbcra.com/lebac_usd'
leliqs_usd = 'https://api.estadisticasbcra.com/leliq_usd'
leliqs_tasa = 'https://api.estadisticasbcra.com/tasa_leliq'
M2varmensual = 'https://api.estadisticasbcra.com/m2_privado_variacion_mensual'
cer = 'https://api.estadisticasbcra.com/cer'
uva = 'https://api.estadisticasbcra.com/uva'
uvi = 'https://api.estadisticasbcra.com/uvi'
tasa_badlar = 'https://api.estadisticasbcra.com/tasa_badlar'
tasa_baibar = 'https://api.estadisticasbcra.com/tasa_baibar '
tasa_TM20 = 'https://api.estadisticasbcra.com/tasa_tm20'
tasa_paseactivas1d = 'https://api.estadisticasbcra.com/tasa_pase_activas_1_dia'
tasa_pasepasivas1d = 'https://api.estadisticasbcra.com/tasa_pase_pasivas_1_dia'
limiteinferior_nointervencion = 'https://api.estadisticasbcra.com/zona_de_no_intervencion_cambiaria_limite_inferior'
limitesuperior_nointervencion = 'https://api.estadisticasbcra.com/zona_de_no_intervencion_cambiaria_limite_superior'
inflacion_mensual = 'https://api.estadisticasbcra.com/inflacion_mensual_oficial'
inflacion_interanual = 'https://api.estadisticasbcra.com/inflacion_interanual_oficial'
inflacion_esperada = 'https://api.estadisticasbcra.com/inflacion_esperada_oficial'
inflacion_diffinteresp = 'https://api.estadisticasbcra.com/dif_inflacion_esperada_vs_interanual'
base_varinter = 'https://api.estadisticasbcra.com/var_base_monetaria_interanual'
base_varinter_usd = 'https://api.estadisticasbcra.com/var_usd_interanual'
usd_official_varinter = 'https://api.estadisticasbcra.com/var_usd_oficial_interanual'
merval_varinter = 'https://api.estadisticasbcra.com/var_merval_interanual'
usd_var_annual = 'https://api.estadisticasbcra.com/var_usd_anual'
usd_var_annual_official = 'https://api.estadisticasbcra.com/var_usd_of_anual'
merval_varannual = 'https://api.estadisticasbcra.com/var_merval_anual'
merval = 'https://api.estadisticasbcra.com/merval'
merval_usd = 'https://api.estadisticasbcra.com/merval_usd'

