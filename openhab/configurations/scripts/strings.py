urls = {
	'home': 'https://hydroottawa.com/',
	'predict': 'https://secure.hydroottawa.com/Usage/Secure/Prediction/PredictMyBill.aspx',
	'usage': 'https://secure.hydroottawa.com/Usage/Secure/TOU/TOUHome.aspx',
	'tsi': 'https://api.teksavvy.com/web/Usage/UsageSummaryRecords?$filter=IsCurrent%20eq%20true'
}
ids = {
	'username': 'topemail',
	'password': 'toppassword',
	'predict': {
		'amount': 'ContentPlaceHolder1_cph_lblTotalAmt',
		'period': 'ContentPlaceHolder1_cph_pnlPrediction'
	},
	'usage': {
		'table': 'ContentPlaceHolder1_mainContent_Main1_lblDailyView',
		'cell': 'ContentPlaceHolder1_mainContent_Main1_lblDaily%sCost'
	}
}
xpaths = {
	'signin': '//form[@id="login-form"]//button[@type="submit"]'
}
scripts = {
	'signin': 'SSO.login()'
}
tests = {
	'home_initial': ids['username'],
	'home_loggedin': 'Sign Out',
	'asp_loggedin': 'Page_Validators',
	'predict': ids['predict']['amount'],
	'usage': ids['usage']['table']
}


