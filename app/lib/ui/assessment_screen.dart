import 'package:flutter/material.dart';

import '../session/session_repository.dart';

/// Pre-assessment form: FSL confidence, signs known, optional demographics.
/// Post-assessment form: same + SUS (10-item) + open feedback.
///
/// Phase 8, Task 11.
class AssessmentScreen extends StatefulWidget {
  final bool isPost;

  const AssessmentScreen({
    super.key,
    this.isPost = false,
  });

  @override
  State<AssessmentScreen> createState() => _AssessmentScreenState();
}

class _AssessmentScreenState extends State<AssessmentScreen> {
  late PageController _pageController;
  int _currentPage = 0;

  // Pre-assessment
  int? _fslConfidence;
  int? _signsKnown;
  String? _ageGroup;
  String? _gender;

  // Post-assessment (same as pre +)
  List<int> _susResponses = List.filled(10, 0);
  String _openFeedback = '';

  bool get _preFormComplete =>
      _fslConfidence != null &&
      _signsKnown != null;

  bool get _postFormComplete =>
      _preFormComplete &&
      _susResponses.every((r) => r != 0) &&
      _openFeedback.isNotEmpty;

  bool get _formComplete =>
      widget.isPost ? _postFormComplete : _preFormComplete;

  @override
  void initState() {
    super.initState();
    _pageController = PageController();
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  Future<void> _saveAssessment() async {
    if (!_formComplete) return;

    final responses = {
      'fslConfidence': _fslConfidence,
      'signsKnown': _signsKnown,
      if (_ageGroup != null) 'ageGroup': _ageGroup,
      if (_gender != null) 'gender': _gender,
      if (widget.isPost) ...{
        'susScores': _susResponses,
        'openFeedback': _openFeedback,
      }
    };

    try {
      await SessionRepository.instance.saveAssessment(
        type: widget.isPost ? 'post' : 'pre',
        responses: responses,
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(widget.isPost
                ? 'Salamat sa pagkumpleto ng post-assessment!'
                : 'Salamat sa pagkumpleto ng pre-assessment!'),
          ),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error saving assessment: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.isPost ? 'Post-Assessment' : 'Pre-Assessment'),
        centerTitle: true,
      ),
      body: PageView(
        controller: _pageController,
        onPageChanged: (i) => setState(() => _currentPage = i),
        children: [
          _PreAssessmentPage(
            fslConfidence: _fslConfidence,
            onFslConfidenceChanged: (v) =>
                setState(() => _fslConfidence = v),
            signsKnown: _signsKnown,
            onSignsKnownChanged: (v) => setState(() => _signsKnown = v),
            ageGroup: _ageGroup,
            onAgeGroupChanged: (v) => setState(() => _ageGroup = v),
            gender: _gender,
            onGenderChanged: (v) => setState(() => _gender = v),
          ),
          if (widget.isPost)
            _PostAssessmentPage(
              susResponses: _susResponses,
              onSusResponsesChanged: (responses) =>
                  setState(() => _susResponses = responses),
              openFeedback: _openFeedback,
              onOpenFeedbackChanged: (v) =>
                  setState(() => _openFeedback = v),
            ),
        ],
      ),
      bottomNavigationBar: BottomAppBar(
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            if (_currentPage > 0)
              TextButton(
                onPressed: () => _pageController.previousPage(
                  duration: const Duration(milliseconds: 300),
                  curve: Curves.easeInOut,
                ),
                child: const Text('Balik'),
              )
            else
              const SizedBox(width: 88),
            Text(
              '${_currentPage + 1}/${widget.isPost ? 2 : 1}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            if (_currentPage < (widget.isPost ? 1 : 0))
              TextButton(
                onPressed: _preFormComplete
                    ? () => _pageController.nextPage(
                          duration: const Duration(milliseconds: 300),
                          curve: Curves.easeInOut,
                        )
                    : null,
                child: const Text('Susunod'),
              )
            else
              FilledButton(
                onPressed: _formComplete ? _saveAssessment : null,
                child: const Text('Ipon'),
              ),
          ],
        ),
      ),
    );
  }
}

class _PreAssessmentPage extends StatelessWidget {
  final int? fslConfidence;
  final Function(int) onFslConfidenceChanged;
  final int? signsKnown;
  final Function(int) onSignsKnownChanged;
  final String? ageGroup;
  final Function(String?) onAgeGroupChanged;
  final String? gender;
  final Function(String?) onGenderChanged;

  const _PreAssessmentPage({
    required this.fslConfidence,
    required this.onFslConfidenceChanged,
    required this.signsKnown,
    required this.onSignsKnownChanged,
    required this.ageGroup,
    required this.onAgeGroupChanged,
    required this.gender,
    required this.onGenderChanged,
  });

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          'Pre-Assessment',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 24),
        _LikertQuestion(
          question: 'Gaano ka-kumpiyansa sa iyong FSL skills?',
          value: fslConfidence,
          onChanged: onFslConfidenceChanged,
          labels: const ['Hindi kumpiyansa', 'Kumpiyansa'],
        ),
        const SizedBox(height: 24),
        _LikertQuestion(
          question: 'Ilang sign ang alam mo na?',
          value: signsKnown,
          onChanged: onSignsKnownChanged,
          labels: const ['Walang', 'Marami'],
        ),
        const SizedBox(height: 24),
        Text(
          'Demographics (Optional)',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 12),
        _DropdownField(
          label: 'Age Group',
          value: ageGroup,
          items: const [
            '<13',
            '13-17',
            '18-25',
            '26-35',
            '36-50',
            '>50',
          ],
          onChanged: onAgeGroupChanged,
        ),
        const SizedBox(height: 16),
        _DropdownField(
          label: 'Gender',
          value: gender,
          items: const [
            'Male',
            'Female',
            'Non-binary',
            'Prefer not to say',
          ],
          onChanged: onGenderChanged,
        ),
        SizedBox(height: MediaQuery.of(context).padding.bottom + 24),
      ],
    );
  }
}

class _PostAssessmentPage extends StatefulWidget {
  final List<int> susResponses;
  final Function(List<int>) onSusResponsesChanged;
  final String openFeedback;
  final Function(String) onOpenFeedbackChanged;

  const _PostAssessmentPage({
    required this.susResponses,
    required this.onSusResponsesChanged,
    required this.openFeedback,
    required this.onOpenFeedbackChanged,
  });

  @override
  State<_PostAssessmentPage> createState() => _PostAssessmentPageState();
}

class _PostAssessmentPageState extends State<_PostAssessmentPage> {
  late TextEditingController _feedbackController;

  @override
  void initState() {
    super.initState();
    _feedbackController = TextEditingController(text: widget.openFeedback);
  }

  @override
  void dispose() {
    _feedbackController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const susQuestions = [
      'Ang app ay madaling gamitin.',
      'Kailangan ng teknikal na suporta upang gamitin ang app.',
      'Ang mga feature ay mahusay na integrated.',
      'Maraming inconsistencies sa app.',
      'Karamihan sa mga tao ay mabilis matututo ng app na ito.',
      'Ang app ay nakakalito.',
      'Ang app ay pakiramdam na mahusay.',
      'Hindi ako kumpiyansa sa paggamit ng app.',
      'Nag-master ako ng app nang mabilis.',
      'Kailangan ko ng maraming pagsasanay bago magsimula.',
    ];

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          'Post-Assessment',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 12),
        Text(
          'System Usability Scale (SUS)',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 16),
        ...List.generate(
          susQuestions.length,
          (i) => Padding(
            padding: const EdgeInsets.only(bottom: 24),
            child: _LikertQuestion(
              question: susQuestions[i],
              value: widget.susResponses[i] == 0 ? null : widget.susResponses[i],
              onChanged: (v) {
                final updated = List<int>.of(widget.susResponses);
                updated[i] = v;
                widget.onSusResponsesChanged(updated);
              },
              labels: const ['Strongly Disagree', 'Strongly Agree'],
            ),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _feedbackController,
          onChanged: widget.onOpenFeedbackChanged,
          maxLines: 4,
          decoration: InputDecoration(
            labelText: 'Optional: Feedback or comments',
            hintText: 'Kung may karagdagang komento...',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        SizedBox(height: MediaQuery.of(context).padding.bottom + 24),
      ],
    );
  }
}

class _LikertQuestion extends StatelessWidget {
  final String question;
  final int? value;
  final Function(int) onChanged;
  final List<String> labels;

  const _LikertQuestion({
    required this.question,
    required this.value,
    required this.onChanged,
    required this.labels,
  });

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(question, style: Theme.of(context).textTheme.titleSmall),
        const SizedBox(height: 12),
        Column(
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(labels[0],
                      style: Theme.of(context)
                          .textTheme
                          .labelSmall
                          ?.copyWith(color: scheme.onSurfaceVariant)),
                  Text(labels[1],
                      style: Theme.of(context)
                          .textTheme
                          .labelSmall
                          ?.copyWith(color: scheme.onSurfaceVariant)),
                ],
              ),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: List.generate(
                5,
                (i) {
                  final v = i + 1;
                  final selected = value == v;
                  return GestureDetector(
                    onTap: () => onChanged(v),
                    child: Container(
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: selected
                            ? scheme.primary
                            : scheme.surfaceContainerHighest,
                        border: selected
                            ? Border.all(color: scheme.primary, width: 2)
                            : null,
                      ),
                      child: Center(
                        child: Text(
                          '$v',
                          style: TextStyle(
                            color: selected
                                ? Colors.white
                                : scheme.onSurfaceVariant,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _DropdownField extends StatelessWidget {
  final String label;
  final String? value;
  final List<String> items;
  final Function(String?) onChanged;

  const _DropdownField({
    required this.label,
    required this.value,
    required this.items,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return DropdownButtonFormField<String>(
      initialValue: value,
      decoration: InputDecoration(
        labelText: label,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      items: items
          .map((v) => DropdownMenuItem(value: v, child: Text(v)))
          .toList(),
      onChanged: onChanged,
    );
  }
}
