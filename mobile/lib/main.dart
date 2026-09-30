import 'package:flutter/material.dart';

void main() => runApp(const NagarSurakshaApp());
class NagarSurakshaApp extends StatelessWidget {
  const NagarSurakshaApp({super.key});
  @override Widget build(BuildContext context) => MaterialApp(
    title:'Nagar Suraksha', theme:ThemeData(useMaterial3:true,colorSchemeSeed:Colors.indigo),
    home:const HomePage());
}
class HomePage extends StatelessWidget {
  const HomePage({super.key});
  @override Widget build(BuildContext context) => Scaffold(
    appBar:AppBar(title:const Text('Nagar Suraksha')),
    body:ListView(padding:const EdgeInsets.all(20),children:[
      const Text('Community Safety Reporting',style:TextStyle(fontSize:24,fontWeight:FontWeight.bold)),
      const SizedBox(height:8), const Text('Report suspected activity for authorised review. Reports are allegations until verified.'),
      const SizedBox(height:24),
      FilledButton.icon(onPressed:()=>Navigator.push(context,MaterialPageRoute(builder:(_)=>const ReportPage())),icon:const Icon(Icons.add_location_alt),label:const Text('Report activity')),
      const SizedBox(height:12), OutlinedButton.icon(onPressed:(){},icon:const Icon(Icons.map),label:const Text('View public map')),
    ]));
}
class ReportPage extends StatefulWidget { const ReportPage({super.key}); @override State<ReportPage> createState()=>_ReportPageState(); }
class _ReportPageState extends State<ReportPage>{ String cat='suspected_drug'; final desc=TextEditingController(); bool anon=true;
 @override Widget build(BuildContext context)=>Scaffold(appBar:AppBar(title:const Text('New report')),body:ListView(padding:const EdgeInsets.all(20),children:[
  DropdownButtonFormField(value:cat,items:const [DropdownMenuItem(value:'suspected_drug',child:Text('Suspected drug activity')),DropdownMenuItem(value:'illegal_liquor',child:Text('Suspected illegal liquor')),DropdownMenuItem(value:'public_use',child:Text('Public substance use')),DropdownMenuItem(value:'distribution',child:Text('Suspected distribution')),DropdownMenuItem(value:'other',child:Text('Other'))],onChanged:(v)=>setState(()=>cat=v!)),
  const SizedBox(height:16),TextField(controller:desc,maxLines:6,decoration:const InputDecoration(labelText:'What did you observe?',border:OutlineInputBorder(),helperText:'Describe observable facts; avoid identifying or confronting individuals.')),
  SwitchListTile(value:anon,onChanged:(v)=>setState(()=>anon=v),title:const Text('Submit anonymously')),
  const SizedBox(height:12),FilledButton(onPressed:(){ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content:Text('Demo report ready for API submission.')));},child:const Text('Submit report'))
 ])); }
